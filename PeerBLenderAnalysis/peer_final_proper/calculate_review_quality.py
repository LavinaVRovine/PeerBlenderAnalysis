# pouze pocítá kolik ma review slov, jak je dlouhé atp.
import json

import pandas as pd

from Helpers.sqlAlchemy import get_smth
from peer_final_proper.peer_helpers import reformat_peer_df, format_and_clear_peer_answers, concat_review_answers

reviews_df = get_smth("SELECT * FROM review")
# only valid ones? zajímá mě solution is complete?
reviews_df = reviews_df[(reviews_df.status != "prep") & (reviews_df.solution_is_complete == 1)]

#  get IDs to merge later
ids = reviews_df['id'].to_frame()
# expandne assessmenty na dataframe
expanded_assessment_df = reviews_df["assessment"].apply(lambda row: pd.Series(json.loads(row)))

only_reviews = reformat_peer_df(expanded_assessment_df, ids)
only_reviews = format_and_clear_peer_answers(only_reviews)


# sloučí všechny odpovědi do jednoho stringu
review_concatenated = pd.DataFrame(only_reviews.groupby(['id'])['answer'].apply(concat_review_answers))
review_concatenated.reset_index(inplace=True)


words_to_delete = pd.read_csv('data/casta_slova_smazat.csv')

words_to_delete = words_to_delete['word'].tolist()
words_to_delete.append('v')


def calculate_peer_info(df):

    # tady je to dle answers, nicméně jde udělat ještě pohled přes review-----------------------------------------
    df['list_answer'] = df['answer'].str.split(' ')
    # odstran slova
    df['nongeneric_words_list'] = df['list_answer'].apply(lambda x: [item for item in x if item not in words_to_delete])
    # 'odstran prázdné'
    df['nongeneric_words_list'] = df['nongeneric_words_list'].apply(lambda x: list(filter(None, x)))

    df['num_of_words'] = df['nongeneric_words_list'].apply(lambda x: len(x))
    df['nongeneric_words_str'] = df['nongeneric_words_list'].apply(lambda x: ''.join(x))
    df['answer_len'] = df['nongeneric_words_str'].apply(lambda x: len(x))

    df['unique_nongeneric_words_list'] = df['nongeneric_words_list'].apply(lambda x: list(set(x)))
    df['unique_num_of_words'] = df['unique_nongeneric_words_list'].apply(lambda x: len(x))
    df['unique_nongeneric_words_str'] = df['unique_nongeneric_words_list'].apply(lambda x: ''.join(x))
    df['review_len'] = df['unique_nongeneric_words_str'].apply(lambda x: len(x))
    return df


# pohled pres jednotlive otazky - každé review má několik otázek. metriky jsou zde počítány pro každý answer zvast
reviews_with_info = calculate_peer_info(only_reviews)


# only selected columns
view_by_answer = reviews_with_info[['num_of_words', 'answer_len', 'unique_num_of_words', 'review_len']]
# sečtení otázek
view_by_answer = reviews_with_info.groupby('id')[['num_of_words', 'answer_len', 'unique_num_of_words', 'review_len']].sum()
view_by_answer.reset_index(inplace=True)
view_by_answer = view_by_answer.add_prefix('answer_')


# pohled přes review - anweery jsou postaveny za sebou a je analyzovan review jako celek
info_review = calculate_peer_info(review_concatenated)
view_by_review = info_review[['num_of_words', 'answer_len', 'unique_num_of_words', 'review_len']]

view_by_review = view_by_review.add_prefix('review_')

peer_rev_info = pd.concat([view_by_answer, view_by_review], axis=1)

print(peer_rev_info)
peer_rev_info.to_csv('data/peer_review_info.csv')

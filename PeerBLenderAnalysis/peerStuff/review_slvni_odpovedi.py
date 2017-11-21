import pandas as pd
import json
from sqlAlchemy import get_smth
import numpy as np
import datetime
import unicodedata

df = get_smth("SELECT * FROM review")

# only valid ones? zajímá mě solution is complete?
df = df[(df.status != "prep") & (df.solution_is_complete == 1)]



# pro labelování - začátek s rubrikami
df = df[df['submitted_at'] >= datetime.date(2016, 10, 1)]

# expandne assessmenty na dataframe
expanded_df = df["assessment"].apply(lambda row: pd.Series(json.loads(row)))

# vlastně hodí nonnany do leva
def squeeze_nan(x):
    original_columns = x.index.tolist()

    squeezed = x.dropna()
    squeezed.index = [original_columns[n] for n in range(squeezed.count())]

    return squeezed.reindex(original_columns, fill_value=np.nan)


def replace_if_list(val):

    if type(val) is list:
        return np.nan
    else:
        return val


def odstran_diakritiku(row):


    line = row
    line = unicodedata.normalize('NFKD', line)

    output = ''
    for c in line:
        if not unicodedata.combining(c):
            output += c

    return output
# zaměním listy za nan - tzn vše co nejsou odpovědi jsou nana
expanded_df = expanded_df.applymap(replace_if_list)

only_reviews = expanded_df.apply(squeeze_nan, axis=1)

only_reviews = only_reviews.dropna(axis=1, how='all')


# takové to pivotování -> multiindex s id a odpověďmi
only_reviews = only_reviews.stack()

only_reviews = only_reviews.str.lower()
only_reviews = pd.DataFrame(only_reviews)
only_reviews.reset_index(inplace=True)
# vrátí pouze text, někde byly i určité hodnoty hodnocení
only_reviews = only_reviews[~only_reviews[0].astype(str).str.isdigit()]
only_reviews.dropna(inplace=True)

# smaže čísla - nejdou do lower:)
only_reviews[0] = only_reviews[0].str.replace('\d*', '')

only_reviews[0] = only_reviews[0].apply(odstran_diakritiku)


# newline na mezeru
only_reviews[0] = only_reviews[0].str.replace('\\n', ' ')
only_reviews[0] = only_reviews[0].str.replace('\\t', ' ')
# hypertextové odkazy, ale nevezme všechny:(
only_reviews[0] = only_reviews[0].str.replace(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '')

# nealfanumerické znaky - smajlíky, tečky, whathaveyou
only_reviews[0] = only_reviews[0].str.replace('[^a-zA-Z\d\s:]', '')
only_reviews[0] = only_reviews[0].str.replace('[,]', ' ')
only_reviews[0] = only_reviews[0].str.replace('[:]', ' ')
only_reviews[0] = only_reviews[0].str.replace("\'", '')
only_reviews[0] = only_reviews[0].str.strip()

only_reviews[0] = only_reviews[0].astype(str)
only_reviews.rename(columns={'level_0': 'rev_id', 'level_1': 'answer_index', 0: 'answer'}, inplace=True)


def concat_review_answers(series):

    total_answers = series.values
    total_answers = list(total_answers)
    total_answers = ' '.join(total_answers)
    return(total_answers)

# sloučí všechny odpovědi do jednoho stringu
review_concatenated = pd.DataFrame(only_reviews.groupby(['rev_id'])['answer'].apply(concat_review_answers))
review_concatenated.reset_index(inplace=True)


words_to_delete = pd.read_csv('casta_slova_smazat.csv')

words_to_delete = words_to_delete['word'].tolist()
words_to_delete.append('v')

def calculate_peer_info(df):

    # tady je to dle answers, nicméně jde udělat ještě pohled přes review-----------------------------------------
    df['list_answer'] = df['answer'].str.split(' ')
    #odstran slova
    df['nongeneric_words_list'] = df['list_answer'].apply(lambda x: [item for item in x if item not in words_to_delete])
    #'odstran prázdné'
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
only_reviews = calculate_peer_info(only_reviews)
view_by_answer = only_reviews[['num_of_words', 'answer_len', 'unique_num_of_words', 'review_len']]
# sečtení otázek
view_by_answer = only_reviews.groupby('rev_id')[['num_of_words', 'answer_len', 'unique_num_of_words', 'review_len']].sum()
view_by_answer.reset_index(inplace=True)
view_by_answer = view_by_answer.add_prefix('answer_')


# pohled přes review - anweery jsou postaveny za sebou a je analyzovan review jako celek
info_review = calculate_peer_info(review_concatenated)
view_by_review = info_review[['num_of_words', 'answer_len', 'unique_num_of_words', 'review_len']]

view_by_review = view_by_review.add_prefix('review_')

#print(view_by_answer)
#(view_by_review)

peer_rev_info = pd.concat([view_by_answer,view_by_review],axis=1)

print(peer_rev_info)
peer_rev_info.to_csv('peer_review_info.csv')
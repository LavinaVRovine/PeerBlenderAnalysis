import collections
import datetime
import json

import pandas as pd

from Helpers.sqlAlchemy import get_smth
from peer_final_proper.peer_helpers import reformat_peer_df, format_and_clear_peer_answers

startTime = datetime.datetime.now()


def return_frequent_words():

    reviews_df = get_smth("SELECT * FROM review")
    ids = reviews_df['id'].to_frame()
    # only valid ones? zajímá mě solution is complete?
    reviews_df = reviews_df[(reviews_df.status != "prep") & (reviews_df.solution_is_complete == 1)]
    # pro labelování - začátek s rubrikami
    # df = df[df['submitted_at'] >= datetime.date(2016, 10, 1)]

    # expandne assessmenty na dataframe
    expanded_assessment_df = reviews_df["assessment"].apply(lambda row: pd.Series(json.loads(row)))

    only_reviews = reformat_peer_df(expanded_assessment_df, ids)

    only_reviews = format_and_clear_peer_answers(only_reviews)

    # tvorba listu, který obsahuje každé slovo
    test_subset = only_reviews["answer"].tolist()
    test_subset = ' '.join(str(v) for v in test_subset)
    test_subset = test_subset.split(' ')

    print('pocet slov je {}'.format(len(test_subset)))
    # dict obsahující slovo:count
    value_count = collections.Counter(test_subset)

    print(type(value_count))
    print(len(value_count))
    print('pocet slov je {}'.format(len(test_subset)))

    print(datetime.datetime.now() - startTime)

    df_casta_slova = pd.DataFrame.from_dict(value_count, orient='index')
    df_casta_slova.reset_index(inplace=True)
    df_casta_slova.rename(columns={0: 'count', 'index': 'word'}, inplace=True)

    df_casta_slova = df_casta_slova[df_casta_slova['count'] >= 100]
    #df_casta_slova.to_csv('casta_slova_smazat.csv')
    print(df_casta_slova)

return_frequent_words()
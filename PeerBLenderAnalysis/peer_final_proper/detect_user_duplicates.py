import json

import pandas as pd

from Helpers.sqlAlchemy import get_smth
from peer_final_proper.peer_helpers import reformat_peer_df, format_and_clear_peer_answers, concat_review_answers


def return_user_duplicates(df):
    duplicated = df[df.duplicated(subset='answer', keep=False)]
    return duplicated


def return_user_duplicate_reviews():

    # get data
    reviews_df = get_smth("SELECT * FROM review")

    # only valid ones? zajímá mě solution is complete?
    reviews_df = reviews_df[(reviews_df.status != "prep") & (reviews_df.solution_is_complete == 1)]
    # pro labelování - začátek s rubrikami


    #  get IDs to merge later
    ids = reviews_df['id'].to_frame()
    # expandne assessmenty na dataframe
    expanded_assessment_df = reviews_df["assessment"].apply(lambda row: pd.Series(json.loads(row)))

    only_reviews = reformat_peer_df(expanded_assessment_df, ids)
    only_reviews.to_csv("reviews_text_subanswers_only.csv", index=False)
    only_reviews = format_and_clear_peer_answers(only_reviews)
    def duplicates_not_concat():
        # jen pro jednonarovou analyzu
        # merge with basic DF to identify users etc
        joined = only_reviews.merge(reviews_df, how='left', left_on='id', right_on='id')
        joined.dropna(inplace=True)
        # vrátí df duplicit usera
        user_duplicates = joined.groupby('reviewed_by_id').apply(return_user_duplicates)
        user_duplicates.reset_index(inplace=True, drop=True)
        print(user_duplicates)

        print("total num of subQs: {}. duplicate len: {}, which is {}%"
              .format(len(only_reviews), len(user_duplicates), (len(user_duplicates)/len(only_reviews)*100)))
        quit()

    duplicates_not_concat()

    # concatenates every answer to one string, ie whole review is one string
    review_concatenated = pd.DataFrame(only_reviews.groupby(['id'])['answer'].apply(concat_review_answers))
    review_concatenated.reset_index(inplace=True)



    # merge with basic DF to identify users etc
    joined = review_concatenated.merge(reviews_df, how='left', left_on='id', right_on='id')

    # vrátí df duplicit usera
    user_duplicates = joined.groupby('reviewed_by_id').apply(return_user_duplicates)
    user_duplicates.reset_index(inplace=True, drop=True)

    user_duplicates['time_spent'] = pd.to_timedelta(user_duplicates.submitted_at - user_duplicates.opened_at).dt.seconds

    return user_duplicates

user_duplicates = return_user_duplicate_reviews()
user_duplicates.to_csv('data/user_self_duplicates_only.csv')
print(user_duplicates)
quit()
duplicit_pocet = user_duplicates.groupby('reviewed_by_id').size()
print(duplicit_pocet.sort_values())
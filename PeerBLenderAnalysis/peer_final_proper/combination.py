import pandas as pd

from Helpers.sqlAlchemy import get_smth

diff_score_df = pd.read_csv('data/different_score_to_mode.csv', encoding='windows-1250')
# redundant columns after join with basic review table
diff_score_df.drop(['Unnamed: 0', 'solution_id', 'reviewed_by_id', 'opened_at',
                    'assessment', 'score', 'notes', 'submitted_at', 'status', 'solution_is_complete'], axis=1, inplace=True)

duplicate_df = pd.read_csv('data/user_self_duplicates_only.csv', encoding='windows-1250')


review_info = pd.read_csv('data/peer_review_info.csv', encoding='windows-1250')
review_info.drop(['Unnamed: 0' ], axis=1, inplace=True)

labeled_reviews = pd.read_excel('C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Skripty/python/peerStuff/review_label.xlsx', sheetname='Sheet2')
reviews_df = get_smth("SELECT * FROM review")


labeled_reviews.dropna(inplace=True)
# every answer is labeled -> avg for solution
labeled_reviews_avg = labeled_reviews.groupby('id')['My_label'].mean()


joined_dfs = pd.merge(reviews_df, review_info, how='left', right_on='answer_id', left_on='id', copy=False)

# join with different score dataframe
joined_dfs = pd.merge(joined_dfs, diff_score_df, how='left', right_on='id', left_on='id' ,copy=False)


# join duplicates------------------------------------------------------------------------------------------------------
duplicate_with_label = pd.DataFrame(duplicate_df['id'])
duplicate_with_label['is_user_duplicate'] = True
joined_dfs = pd.merge(joined_dfs, duplicate_with_label, how='left')
joined_dfs['is_user_duplicate'] = joined_dfs['is_user_duplicate'].fillna(False)


# drop useless / additional index columns
joined_dfs.drop(['answer_id'], axis=1, inplace=True)

print(joined_dfs.columns)
quit()
joined_dfs.to_csv('joined.csv')
print(joined_dfs)
import pandas as pd

from Helpers.sqlAlchemy import get_smth

df = get_smth("SELECT * FROM review")

# only valid ones? zajímá mě solution is complete?
df = df[(df.status != "prep") & (df.solution_is_complete == 1)]

# užít k tomu, co píší do assessmentu
'''
# expandne assessmenty na dataframe
expanded_df = df["assessment"].apply(lambda row: pd.Series(json.loads(row)))
# join s původní DF
df = pd.concat([df, expanded_df], axis=1)
'''

df = df[["score", "reviewed_by_id"]]

comparission = pd.DataFrame(df.groupby(["reviewed_by_id"])["score"].mean())
num_of_revs = df.groupby(["reviewed_by_id"])["reviewed_by_id"].count().rename("num_of_revs")

comparission = pd.concat([comparission, num_of_revs], axis = 1)
avg = df.score.mean()


comparission["avg"] = avg
comparission["diff"] = comparission["avg"] - comparission["score"]
comparission.sort_values(["diff"], axis = 0, inplace=True)
print(comparission)


# vzít několik standarních odchylek?
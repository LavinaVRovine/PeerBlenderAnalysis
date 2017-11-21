import pandas as pd
from scipy import stats
from sqlAlchemy import get_smth

#počítá kolikrát a kolik % student hodnotí jinak, nežli je modus hodnocení

df = get_smth("SELECT * FROM review")

# only valid ones? zajímá mě solution is complete?
df = df[(df.status != "prep") & (df.solution_is_complete == 1)]


rev_count = pd.DataFrame(df.groupby('solution_id')["score"].count())
num_of_revs_by_stud = pd.DataFrame(df.groupby('reviewed_by_id')["score"].count())

# pocita modus - k zjištění typycké hodnoty. následně se identifikují ti, kteří hodnotili jinak
# scipy.stats returns tuple of lists of value and occurence ([val],[ocur]), then split to 2series
mode_operations = pd.DataFrame(df.groupby('solution_id')["score"].apply(lambda x: stats.mode(x)))
mode_operations = mode_operations.score.apply(pd.Series)

solution_info = pd.concat([rev_count, mode_operations], axis=1)

solution_info.columns = ["num_of_revs", "mode_val", "mode_occur"]
# list to value only
solution_info["mode_val"] = solution_info["mode_val"].apply(lambda x: x[0])
solution_info["mode_occur"] = solution_info["mode_occur"].apply(lambda x: x[0])
solution_info.reset_index(inplace=True)


def solution_status(df):
    if df["num_of_revs"] < 5:
        return "not_enough_revs"
    elif df["kolik_proc_je_jinak"] >= 0.25:
        return "prolly_kontroversial"
    else:
        return "alright"

solution_info["kolik_proc_je_jinak"] = \
    (solution_info["num_of_revs"] - solution_info["mode_occur"]) / solution_info["num_of_revs"]

# identifikuje se, jak je na tom vlastne review - mohu s ním počítat dále?
solution_info["review_status"] = solution_info.apply(solution_status, axis = 1)
#najoinování základních dat s vypočteným modusem
joined = pd.merge(df,solution_info, left_on="solution_id", right_on="solution_id")

# identifikuj, jestli je score jine jak modus
joined["is_diff_score"] = True
joined.loc[joined['score'] == joined['mode_val'],"is_diff_score"] = False

# sline only rozdílné solutiony
joined_diff_only = joined[joined["is_diff_score"] == True]

# počet rozdílných hodnocení
num_of_diff_score = pd.DataFrame(joined_diff_only.groupby(['reviewed_by_id'])["is_diff_score"].count())

# joinni pocet hodnoceni studenta a vypočítej kolik je to procent
num_of_diff_score = pd.concat([num_of_diff_score, num_of_revs_by_stud], axis=1)
num_of_diff_score.fillna(value=0, inplace=True)
num_of_diff_score["pct_different_scores"] = (num_of_diff_score['is_diff_score'] / num_of_diff_score['score']) * 100

# quick sort
num_of_diff_score.sort_values(["is_diff_score"], axis = 0, inplace=True, ascending=False)

print(num_of_diff_score)
print(joined[joined["solution_id"] == 10])
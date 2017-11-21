import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from Helpers.sqlAlchemy import get_smth

# počítá kolikrát a kolik % student hodnotí jinak, nežli je modus hodnocení
desired_width = 320
pd.set_option('display.width', desired_width)

#df = get_smth("SELECT * FROM review")
df = get_smth('SELECT *, CO.id as cid FROM diplomkatest.review AS REV JOIN diplomkatest.solution AS SOL ON REV.solution_id=SOL.id join diplomkatest.unit AS UN ON SOL.unit_id=UN.id JOIN diplomkatest.course as CO ON UN.course_id=CO.id')

# only valid ones? zajímá mě solution is complete?
df = df[(df.status != "prep") & (df.solution_is_complete == 1)]

num_of_revs_by_stud = pd.DataFrame(df.groupby('reviewed_by_id')["score"].count())


def determine_solution_status(df):
    if df["num_of_revs"] < 5:
        return "not_enough_revs"

    elif df["kolik_proc_je_jinak"] >= 0.2 and df["kolik_proc_je_jinak"] <= 0.6:
        return "prolly_kontroversial"

    else:
        return "alright"


# modues,occurences and stuff
def get_basic_review_stats(df):
    total_review_count = pd.DataFrame(df.groupby('solution_id')["score"].count())

    # pocita modus - k zjištění typycké hodnoty. následně se identifikují ti, kteří hodnotili jinak
    # scipy.stats returns tuple of lists of value and occurence ([val],[ocur]), then split to 2series
    mode_operations = pd.DataFrame(df.groupby('solution_id')["score"].apply(lambda x: stats.mode(x)))
    mode_operations = mode_operations.score.apply(pd.Series)

    solution_info = pd.concat([total_review_count, mode_operations], axis=1)
    solution_info.columns = ["num_of_revs", "mode_value", "mode_occurrence"]

    # list to value only
    solution_info["mode_value"] = solution_info["mode_value"].apply(lambda x: x[0])
    solution_info["mode_occurrence"] = solution_info["mode_occurrence"].apply(lambda x: x[0])
    solution_info.reset_index(inplace=True)
    solution_info["kolik_proc_je_jinak"] = \
        (solution_info["num_of_revs"] - solution_info["mode_occurrence"]) / solution_info["num_of_revs"]
    # identifikuje se, jak je na tom vlastne review - mohu s ním počítat dále?
    solution_info["review_status"] = solution_info.apply(determine_solution_status, axis=1)
    return solution_info


def get_review_with_mode_distance(df):
    solution_info = get_basic_review_stats(df)

    # najoinování základních dat s vypočteným modusem
    joined = pd.merge(df, solution_info, left_on="solution_id", right_on="solution_id")

    # identifikuj, jestli je score jine jak modus
    joined["is_diff_score"] = True
    joined.loc[joined['score'] == joined['mode_value'], "is_diff_score"] = False

    joined['score_mode_distance'] = abs(joined['score'] - joined['mode_value'])
    return joined



# calculates how often student scores differently than the other reviewers
def calculate_student_different_score_occurence(joined):

    # slice only rozdílné solutiony a kontroverzní
    joined_diff_only = joined[(joined["is_diff_score"] == True) & (joined['review_status'] == 'prolly_kontroversial')]
    # počet rozdílných hodnocení
    num_of_diff_score_by_reviewer = pd.DataFrame(joined_diff_only.groupby(['reviewed_by_id'])["is_diff_score"].count())

    # joinni pocet hodnoceni studenta a vypočítej kolik je to procent
    num_of_diff_score_by_reviewer = pd.concat([num_of_diff_score_by_reviewer, num_of_revs_by_stud], axis=1)
    num_of_diff_score_by_reviewer.fillna(value=0, inplace=True)
    num_of_diff_score_by_reviewer["pct_different_scores"] = \
        (num_of_diff_score_by_reviewer['is_diff_score'] / num_of_diff_score_by_reviewer['score']) * 100

    # quick sort
    num_of_diff_score_by_reviewer.sort_values(["is_diff_score"], axis=0, inplace=True, ascending=False)
    return num_of_diff_score_by_reviewer


joined = get_review_with_mode_distance(df)


joined.drop(['opened_at', 'status', 'solution_is_complete', 'assessment', 'notes', 'submitted_at',
             'footer', 'contact_email', 'upload_max_filesize_kb', 'ga_code', 'dir', 'name', 'goals',
             'support', 'generator','def','rubrics', 'reading', 'methods','review_count', 'def',
             'objections_since','finalized_since', 'reviews_since', 'published_since', 'answer','edited_at',
             'attachment','assignment_id', 'unit_id', 'user_id', 'reviewed_by_id', 'id',
             'kolik_proc_je_jinak', 'num_of_revs', 'solution_id', 'course_id'], axis=1, inplace=True)

joined = joined[(joined['cid']== 2) | (joined['cid']==5 )]

print(joined.groupby('cid').score.describe())


joined = joined[joined['review_status']!= "not_enough_revs"]

different_only = joined[joined['is_diff_score'] == True]

count_2 = len(joined[joined['cid']== 2])
count_5 = len(joined[joined['cid']== 5])

count_diff_2 = len(different_only[different_only['cid']== 2])
count_diff_5 = len(different_only[different_only['cid']== 5])

print("Total len for course2: {}, number of revs different then mode: {}, which is {}%"
      .format(count_2, count_diff_2, round(count_diff_2/count_2*100),2))
print("Total len for course5: {}, number of revs different then mode: {}, which is {}%"
      .format(count_5, count_diff_5, round(count_diff_5/count_5*100),2))



print(different_only.groupby('cid').describe())
joined.groupby("cid").boxplot(column="score")
plt.show()


print(joined.groupby('cid').describe())

joined.to_csv("mode_diff.csv")
#print(joined)
#print(joined.groupby('cid').describe())
# filter only big distances between score and modus
# joined = joined[joined['sco
import pandas as pd
from Helpers.sqlAlchemy import get_smth
from logy import dny_lognuti, time_spent

desired_width = 320
pd.set_option('display.width', desired_width)

# for log labeling





# connect to data
#df = pd.read_csv("C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Data_od_Honzy_Martinka/log.csv.gz",
#                 compression='gzip', sep="\t")

df = pd.read_csv('C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Skripty/python/logy/labeled_logs.csv', encoding='utf-8')

# první řádek je fail
df.drop([0], inplace=True)
df.dropna(inplace=True)

# change to datetime from str
df["log_date_time"] = pd.to_datetime(df.loc[:, "logged_at"])

# time vars
# +1, becaouse 0= monday,
df["week_day"] = df.loc[:, "log_date_time"].dt.dayofweek + 1
df['week_num'] = df.loc[:, "log_date_time"].dt.weekofyear
df['year'] = df.loc[:, "log_date_time"].dt.year
df['year_week'] = df['year'].astype(str) + "_" + df['week_num'].astype(str)
# divno multiplo záznamy
df.drop_duplicates(subset=['user_id', 'logged_at'], inplace=True)




def get_yw_log_stats(df):
    # calculate for year week
    actions_logins = dny_lognuti.get_actions_and_logins(df)
    time_spent_df = time_spent.calculate_time_spent(df)

    joined_yw = pd.merge(actions_logins, time_spent_df, on='user_yw')

    # nvm aktuálně jak s tím
    joined_yw.loc[joined_yw['probably_valid'] == False, 'time_diff'] = joined_yw['time_diff'].quantile(q=0.5)
    return joined_yw

def get_unit_log_stats(labeled_logs):
    # calculate for year week
    # calculate for every unit
    actions_unit = dny_lognuti.get_actions_for_units(labeled_logs)
    time_spent_units = time_spent.calculate_time_spent_by_unit(labeled_logs)
    actions_unit['user_unit'] = actions_unit['user_id'].astype(str) + "_" + \
                                actions_unit['corresponding_unit'].astype(str)
    time_spent_units['user_unit'] = time_spent_units['user_id'].astype(str) + "_" + \
                                    time_spent_units['corresponding_unit'].astype(str)

    joined_unit = pd.merge(actions_unit, time_spent_units, on='user_unit')
    # nvm aktuálně jak s tím
    joined_unit.loc[joined_unit['probably_valid'] == False, 'time_diff'] = joined_unit['time_diff'].quantile(q=0.5)

    unit_course_ids = get_smth('SELECT U.id as unit_id, U.course_id as course_id  FROM diplomkatest.unit as U')
    joined_unit = joined_unit.merge(unit_course_ids, how='left', left_on='corresponding_unit_x', right_on='unit_id')
    #joined_unit.drop(['sol_id', 'unit_id', 'rev_id'], axis=1, inplace=True)
    # není třeba, pokud budu mít všechna data
    joined_unit['course_id'].fillna(method='ffill', inplace=True)

    joined_unit['spent_time_seconds'] = pd.to_timedelta(joined_unit.loc[:, "time_diff"])
    joined_unit['spent_time_seconds'] = joined_unit['spent_time_seconds'].dt.total_seconds()
    joined_unit['user_course_id'] = joined_unit['user_id_x'].astype(str) + "_" + \
                                    joined_unit['course_id'].astype(str)



    joined_unit = joined_unit[joined_unit['probably_valid'] == True]

    enrollment = get_smth('SELECT user_id, course_id, role FROM diplomkatest.enrollment')
    enrollment = enrollment[enrollment['role'] == 'student']
    enrollment.drop(['role'], axis=1, inplace=True)
    enrollment['user_course_id'] = enrollment['user_id'].astype(str) + "_" + enrollment['course_id'].astype(str)

    # vlastně vyfiltruji nestudenty
    joined_unit = pd.merge(joined_unit, enrollment, on='user_course_id')


    joined_unit.to_csv('data/logs_with_course-all_labels.csv')
    return joined_unit


def get_user_unit_stats():
    return unit_stats

df.dropna(inplace=True)
unit_stats = get_unit_log_stats(df)

unit_stats.drop(['user_id_y', 'corresponding_unit_y'], axis=1, inplace=True)
yw_stats = get_yw_log_stats(df)

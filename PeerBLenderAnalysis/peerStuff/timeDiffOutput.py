# bere data z timeDiffs

import numpy as np
import pandas as pd

df = pd.read_csv('timeUserRevSpent.csv')

df.rename(columns={'entity_identifier': "review_id"}, inplace=True)

df['time_spent_timedelta'] = pd.to_timedelta(df['cum_sum'])


def just_mean(df):
    return df.mean()
#funkce možná nefunguje; nejde totiž o funkci, ale něco jako komentář aby se nespouštělo. Proč? nevím:D
def total_avg_stud():
    avg_timespent = df.time_spent_timedelta.mean()
    median_timespent = df.time_spent_timedelta.median()

    print(avg_timespent)
    print(median_timespent)
    print(df.time_spent_timedelta.describe())





    student_vs_avg = pd.DataFrame(df.groupby(['user_id'])['time_spent_timedelta'].apply(just_mean))
    student_vs_avg.reset_index(inplace=True)
    student_vs_avg['diff_minutes'] = (avg_timespent/np.timedelta64(1, 's') -
                              student_vs_avg['time_spent_timedelta']/np.timedelta64(1, 's'))/60

    # days_of_week_logged proč, ale normálně v DF vracelo NaNs
    wtf = df.groupby(['user_id']).size().rename('count')
    student_vs_avg = student_vs_avg.join(wtf, on='user_id')
    student_vs_avg.sort_values('diff_minutes', inplace=True)

# daný unit vs ostatní v unitu
from Helpers.sqlAlchemy import get_smth
solutions  = get_smth("SELECT * FROM solution")

unit_avg = pd.DataFrame(df.groupby(['corresponding_unit_id'])['time_spent_timedelta'].apply(just_mean))
student_unit_avg = pd.DataFrame(df.groupby(['user_id','corresponding_unit_id'])['time_spent_timedelta'].apply(just_mean))
student_unit_avg.reset_index(inplace=True)
student_unit_avg = student_unit_avg.join(unit_avg, on='corresponding_unit_id', lsuffix='l',rsuffix='r')

student_unit_avg.rename(columns={'time_spent_timedeltar' : 'unit_avg', 'time_spent_timedeltal' : 'student_unit_avg'},
                        inplace=True)
student_unit_avg['time_diff'] = (student_unit_avg['student_unit_avg']/np.timedelta64(1, 's')
                                 - student_unit_avg['unit_avg']/np.timedelta64(1, 's'))\
                                /60
print(student_unit_avg.sort_values('time_diff'))
import pandas as pd

from Helpers.sqlAlchemy import get_smth
from ews_and_anomalydeterction import anomalies, score, slope
from student_classification import classify_students

desired_width = 320
pd.set_option('display.width', desired_width)

def get_user_course_unit_info():
    """počítá avg score
    :returns df
    """
    with open("C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Skripty/avg_body_by_solution.sql", encoding='utf-8') as file:
        sql_body_command = file.read()

    solution_scores = get_smth(sql_body_command)
    solution_scores['fuck'] = solution_scores['user_id'].astype('str') + "_"  +solution_scores['unit_id'].astype('str')
    vse_ostatní = get_smth('SELECT USER.id as user_id, USER.name as user_name, COURSE.id as course_id, UN.id AS unit_id, UN.def as def FROM diplomkatest.user as USER JOIN diplomkatest.enrollment as ROLL ON USER.id = ROLL.user_id JOIN diplomkatest.course AS COURSE ON ROLL.course_id = COURSE.id JOIN diplomkatest.unit AS UN ON COURSE.id=UN.course_id')
    vse_ostatní['fuck'] = vse_ostatní['user_id'].astype('str') + "_" + vse_ostatní['unit_id'].astype('str')

    #dropnutí exams
    vse_ostatní['def'] = vse_ostatní['def'].str.lower()
    vse_ostatní = vse_ostatní[~vse_ostatní['def'].str.contains('test')]
    vse_ostatní = vse_ostatní[~vse_ostatní['def'].str.contains('exam')]

    # hmm days_of_week_logged, dropnu taky?
    vse_ostatní = vse_ostatní[~vse_ostatní['def'].str.contains('exam')]


    joined = pd.merge(vse_ostatní, solution_scores, how='left', left_on='fuck', right_on='fuck')
    # užito pokud solution odevzda, ale neobdržel hodnocení
    joined.loc[~joined['solution_id'].isnull(),'avg_score'] =\
        joined.loc[~joined['solution_id'].isnull(),'avg_score'].fillna(0)
    joined.to_csv('data/student_unit_course-classfic_score_slove.csv')
    return joined

joined = get_user_course_unit_info()

# student-course only
classified_df = classify_students(joined)
# add ID for join
classified_df['user_course_id'] = classified_df['user_id'].astype(str) + "_" + classified_df['course_id'].astype(str)


scored_df = score.score_status(joined)
scored_df['user_course_id'] = scored_df['user_id_x'].astype(str) + "_" + scored_df['course_id'].astype(str)


slope_df = slope.get_slopes(joined)
slope_df['user_course_id'] = slope_df['user_id_x'].astype(str) + "_" + slope_df['course_id'].astype(str)


final = pd.merge(classified_df, scored_df, how='inner', on='user_course_id', copy=False)


final = pd.merge(final, slope_df, how='inner', on='user_course_id',copy=False)


final.drop(['user_id_x_x', 'course_id_y', 'user_id_x_y','course_id'], axis=1, inplace=True)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
final.to_csv('data/student_course-classific_score_slope.csv')
def get_user_course_info():
    return final

# student-course-unit
anomaly_df = anomalies.get_anomalies(joined)
anomaly_df.to_csv('data/anomaly_detection.csv')

import numpy as np

"""
with open("C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Skripty/avg_body_by_solution.sql", encoding='utf-8') as file:
    sql_body_command = file.read()


solution_scores = get_smth(sql_body_command)
solution_scores['fuck'] = solution_scores['user_id'].astype('str') + "_"  +solution_scores['unit_id'].astype('str')
vse_ostatní = get_smth('SELECT USER.id as user_id, USER.name as user_name, COURSE.id as course_id, UN.id AS unit_id, UN.def as def FROM diplomkatest.user as USER JOIN diplomkatest.enrollment as ROLL ON USER.id = ROLL.user_id JOIN diplomkatest.course AS COURSE ON ROLL.course_id = COURSE.id JOIN diplomkatest.unit AS UN ON COURSE.id=UN.course_id')
vse_ostatní['fuck'] = vse_ostatní['user_id'].astype('str') +"_" + vse_ostatní['unit_id'].astype('str')

#dropnutí exams
vse_ostatní['def'] = vse_ostatní['def'].str.lower()
vse_ostatní = vse_ostatní[~vse_ostatní['def'].str.contains('test')]
vse_ostatní = vse_ostatní[~vse_ostatní['def'].str.contains('exam')]

# hmm days_of_week_logged, dropnu taky?
vse_ostatní = vse_ostatní[~vse_ostatní['def'].str.contains('exam')]


joined = pd.merge(vse_ostatní, solution_scores, how='left', left_on='fuck', right_on='fuck')
#joined = joined[joined['user_id_x'] == 45]
# užito pokud solution odevzda, ale neobdržel hodnocení
joined.loc[~joined['solution_id'].isnull(),'avg_score'] =\
    joined.loc[~joined['solution_id'].isnull(),'avg_score'].fillna(0)
# aktuálně nevím, jak identifikovat unity bez assessmentu, takže všechno dropnu, Fit

# joined.dropna(inplace=True)

"""


def determine_warn_status(df):
    """decides how well student is doing based on distance from points he should have
    :arg df with calculated distance from minimum points required
    :returns labeled DF
    """
    df.loc[df['point_distance'] >= 0.5, 'ward_status'] = 'Not doing well'
    df.loc[df['point_distance'] <= -0.5, 'ward_status'] = 'Probably OK'
    df.loc[(df['point_distance'] > -0.5) & (df['point_distance'] < 0.5), 'ward_status'] = 'Living on the edge'
    df.loc[df['achieved_minimum_points'] == True, 'warn_status_points'] = 'Achieved minimum'
    df.reset_index(inplace=True)

    return df


def score_status(joined):
    """labels students based on distance from minimum about of points they should have atm.
    :arg student-course-unit-scores df
    :returns labeled df user-course
    """

    test = joined.groupby(['user_id_x', 'course_id'])['avg_score'].agg({'sum': np.sum, 'should_have_num_sols': np.size, 'avg_score':np.mean})
    test['size'] = joined.groupby(['user_id_x', 'course_id'])['avg_score'].count()

    test['should_have'] = test['should_have_num_sols'] * 1.75
    test['point_distance'] = test['should_have'] - test['sum']

    # nemá smysl zobrazovat ty, kteří už mají potřebné minimum bodů, whatever that is
    test['achieved_minimum'] = False
    minimum = 18
    test.loc[test['sum'] >= minimum, 'achieved_minimum'] = True
    test.rename(columns={'sum': 'pocet_bodu', 'size':'pocet_ukolu', 'should_have': 'should_have_points',
                          'achieved_minimum' : 'achieved_minimum_points'}, inplace=True)
    output = determine_warn_status(test)
    return output

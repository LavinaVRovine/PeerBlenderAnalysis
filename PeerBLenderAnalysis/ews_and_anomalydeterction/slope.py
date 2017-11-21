import numpy as np
import pandas as pd

'''
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

# užito pokud solution odevzda, ale neobdržel hodnocení
joined.loc[~joined['solution_id'].isnull(),'avg_score'] =\
    joined.loc[~joined['solution_id'].isnull(),'avg_score'].fillna(0)
# aktuálně nevím, jak identifikovat unity bez assessmentu, takže všechno dropnu, Fit

print(joined)
'''


def trendline(data, order=1):
    """helper function - calculates the slope for series
    :arg score series for user-course
    :returns scalar slope
    """
    coeffs = np.polyfit(data.index.values, data['avg_score'], order)
    print(data)
    print(coeffs)

    slope = coeffs[-2]
    return float(slope)


def get_slope(user_slice):
    """helper function - for groupby

    :arg user_slice=user-course slice
    :returns series
    """
    user_slice.reset_index(inplace=True)

    if len(user_slice) < 2:
        return pd.Series({'slope': None, 'based_on': len(user_slice)})

    slope = trendline(user_slice)
    return pd.Series({'slope': slope, 'based_on': len(user_slice)})


def calculate_slope(scores_and_allother):
    """helper function - formatting only

    """
    df = pd.DataFrame(scores_and_allother.groupby(['user_id_x', 'course_id']).apply(get_slope))
    df.reset_index(inplace=True)

    return df


def get_slopes(joined):
    """Calculates slope for each student_course
    slope == trend in that course
    :arg student-course-unit-scores df
    :returns labeled df user-course
    """
    wo_nans = joined.dropna(subset=['solution_id'])

    joined.fillna(0, inplace=True)
    all_with_nans = calculate_slope(joined)
    all_with_nans.rename(columns={'based_on': 'based_on_with_nans', 'slope': 'slope_with_nans'}, inplace=True)

    answered = calculate_slope(wo_nans)
    answered.rename(columns={'based_on': 'based_on_wo_nans', 'slope': 'slope_wo_nans'}, inplace=True)

    joined = pd.merge(all_with_nans, answered, how='left', suffixes=("_x", '_y'))
    return joined

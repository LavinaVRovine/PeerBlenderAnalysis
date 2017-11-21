# identifikuje anomálie - tedy když někdo obdrží podivný počet bodu - rozdílný než obvykle
import pandas as pd

'''
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
# aktuálně nevím, jak identifikovat unity bez assessmentu, takže všechno dropnu, Fit


'''
q95 = [0.97, 0.829, 0.71, 0.625, 0.568, 0.526, 0.493, 0.466,
       0.444, 0.426, 0.41, 0.396, 0.384, 0.374, 0.365, 0.356,
       0.349, 0.342, 0.337, 0.331, 0.326, 0.321, 0.317, 0.312,
       0.308, 0.305, 0.301, 0.29
      ]
Q95 = {n:q for n,q in zip(range(3,len(q95)+1), q95)}
def dixon_test(data, left=True, right=True, q_dict=Q95):
    """
    Keyword arguments:
        data = A ordered or unordered list of data points (int or float).
        left = Q-test of minimum value in the ordered list if True.
        right = Q-test of maximum value in the ordered list if True.
        q_dict = A dictionary of Q-values for a given confidence level,
            where the dict. keys are sample sizes N, and the associated values
            are the corresponding critical Q values. E.g.,
            {3: 0.97, 4: 0.829, 5: 0.71, 6: 0.625, ...}

    Returns a list of 2 values for the outliers, or None.
    E.g.,
       for [1,1,1] -> [None, None]
       for [5,1,1] -> [None, 5]
       for [5,1,5] -> [1, None]

    """
    assert (left or right), 'At least one of the variables, `left` or `right`, must be True.'
    assert (len(data) >= 3), 'At least 3 data points are required'
    assert (len(data) <= max(q_dict.keys())), 'Sample size too large'

    sdata = sorted(data)
    Q_mindiff, Q_maxdiff = (0, 0), (0, 0)

    if left:
        Q_min = (sdata[1] - sdata[0])
        try:
            Q_min /= (sdata[-1] - sdata[0])
        except ZeroDivisionError:
            pass
        Q_mindiff = (Q_min - q_dict[len(data)], sdata[0])

    if right:
        Q_max = abs((sdata[-2] - sdata[-1]))
        try:
            Q_max /= abs((sdata[0] - sdata[-1]))
        except ZeroDivisionError:
            pass
        Q_maxdiff = (Q_max - q_dict[len(data)], sdata[-1])

    if not Q_mindiff[0] > 0 and not Q_maxdiff[0] > 0:
        outliers = [None, None]

    elif Q_mindiff[0] == Q_maxdiff[0]:
        outliers = [Q_mindiff[1], Q_maxdiff[1]]

    elif Q_mindiff[0] > Q_maxdiff[0]:
        outliers = [Q_mindiff[1], None]

    else:
        outliers = [None, Q_maxdiff[1]]

    return outliers

def determine_outliers(slice):
    """decides wheter a row is an outlier
    :arg student-course slice

    """
    if len(slice) < 3:
        slice[:] = 'not_enough_samples'
    else:
        dixon_values = dixon_test(slice)
        if dixon_values[0] != None:
            slice[slice == dixon_values[0]] = 'low_outlier'

        elif dixon_values[1] != None:
            slice[slice == dixon_values[1]] = 'high_outlier'

        else:
            slice[:] = 'no_outlier'
    return slice

def get_anomalies(joined):
    """determines if an assessment is an anomaly for given student in given course
    :argstudent-course-unit-scores df
    :returns labeled df - user-course-unit
    """
    #joined.fillna(0, inplace=True)
    joined.loc[:,'avg_score'].fillna(0,inplace=True)

    joined['outlier_status_with_nans'] = joined.groupby(['user_id_x', 'course_id'])['avg_score'].apply(determine_outliers)
    joined_wo_nans = joined.dropna(inplace=False)


    joined_wo_nans['outlier_status_wo_nans'] = joined_wo_nans.groupby(['user_id_x', 'course_id'])['avg_score'].apply(determine_outliers)
    joined = pd.merge(joined, joined_wo_nans, how='left')
    return joined


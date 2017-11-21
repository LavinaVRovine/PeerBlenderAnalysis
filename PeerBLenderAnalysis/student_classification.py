import pandas as pd
import numpy as np

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



#joined = joined[joined['user_id_x'] == 209]

'''






def classify_students(joined):
    """classiffies students based on number of assessments they submited/or should have submited rather
    :argstudent-course-unit-scores df
    :returns labeled df user-course
    """

    def add_avg_time_on_unit(student_course_row_slice):

        def recode_avg_unit_time(mean_time):
            if pd.isnull(mean_time):
                return '-'
            elif mean_time <= 3600:
                return '<=3600s'
            elif mean_time <= 7200:
                return '>3600 & <=7200'
            else:
                return '>7200'



        user_course_id = student_course_row_slice['user_course_id']
        logs = pd.read_csv('data/logs_with_course-all_labels.csv')
        user_course_logs = logs[logs['user_course_id'] == user_course_id]
        avg_time_spent = user_course_logs['spent_time_seconds'].mean()


        return pd.Series({'avg_unit_time_spent':avg_time_spent, 'avg_unit_time_spent_label':recode_avg_unit_time(avg_time_spent),
                          "unit_count" : len(user_course_logs)})


    def student_classify_num_of_sols(student_course_slice):
        """decides student label
        labels - #{f-er = nic nedelal, Sleeper = začal pozdě, NVMer = na konci už nemusel, IamOut = v průběhu to zabalil}
        :arg student-course slice
        :returns scalar label
        """

        if (len(student_course_slice[student_course_slice.isnull()]) == len(student_course_slice)):
            return "Not_ivn_trying"
        elif len(student_course_slice) < 5:
            return "F-er"
        # první value je nula a ostatní - nenany vs všechny - tedy kolek procent ostatních jsou nany; tzn musí mít maximálně
        # 0.199 NaNů
        elif np.isnan(student_course_slice.iat[0]) \
                and (len(student_course_slice[1:][student_course_slice.isnull()]) / len(
                    student_course_slice[1:])) <= 0.2:
            return 'SleeperA'
        elif (np.isnan(student_course_slice.iat[0]) and np.isnan(student_course_slice.iat[1])) \
                and (len(student_course_slice[2:][student_course_slice.isnull()]) / len(
                    student_course_slice[2:])) <= 0.2:
            # jen jeden sleeper B --- > recodovan do Ačka
            return 'SleeperA'
        elif np.isnan(student_course_slice.iat[-1]) \
                and (len(student_course_slice[:-1][student_course_slice.isnull()]) / len(
                    student_course_slice[:-1])) <= 0.2:
            return 'NVMerA'
        elif (np.isnan(student_course_slice.iat[-1]) and np.isnan(student_course_slice.iat[-2])) \
                and (len(student_course_slice[:-2][student_course_slice.isnull()]) / len(
                    student_course_slice[:-2])) <= 0.2:
            # asi 5 NVMersB asi lepsí pouze jeden label pro tyto --- > recodovan do Ačka
            return 'NVMerA'
        elif len(student_course_slice[student_course_slice.isnull()]) / len(student_course_slice) >= 0.55:
            return 'IamOut'
        else:
            return "Otter"

    def weight_mean(student_course_slice):
        # print(student_course_slice)
        mean = student_course_slice.mean()
        return mean
        # print(mean)
        non_nans = student_course_slice.count()
        if non_nans < 5:
            weight = 0.5
        elif non_nans < 10:
            weight = 0.75
        else:
            weight = 1
        return mean * weight


    student_classification = pd.DataFrame(
        joined.groupby(['user_id_x', 'course_id'])['avg_score'].apply(student_classify_num_of_sols))
    student_classification['avg_course_score_weighted'] = \
        joined.groupby(['user_id_x', 'course_id'])['avg_score'].apply(weight_mean)



    student_classification.loc[student_classification['avg_course_score_weighted'] <=
                               student_classification['avg_course_score_weighted'].quantile(q=0.66),
                               'avg_score_classification'] = "b_mid"
    student_classification.loc[student_classification['avg_course_score_weighted'] <=
                               student_classification['avg_course_score_weighted'].quantile(q=0.33),
                               'avg_score_classification'] = "a_low"

    student_classification.loc[student_classification['avg_course_score_weighted'] >
                               student_classification['avg_course_score_weighted'].quantile(q=0.66),
                               'avg_score_classification'] = "c_high"


    student_classification.reset_index(inplace=True)
    student_classification.rename(columns={'avg_score': 'classification_based_on_assignements', 'user_id_x': 'user_id'},
                                  inplace=True)


    student_classification['user_course_id'] = student_classification['user_id'].astype(str) + "_" + \
                                               student_classification['course_id'].astype(
                                                   str)

    student_classification[['avg_unit_time_spent', 'avg_unit_time_spent_label', 'unit_count']] = \
        student_classification.apply(add_avg_time_on_unit, axis=1)

    return student_classification
import pandas as pd

from Helpers.sqlAlchemy import get_smth


def return_num_of_additional_revs():
    df = get_smth('SELECT * FROM review '
                  'JOIN solution ON review.solution_id=solution.id '
                  'JOIN unit ON solution.unit_id = unit.id ')
    # only valid ones? zajímá mě solution is complete?
    df = df[(df.status != "prep") & (df.solution_is_complete == 1)]

    student_unit_data = pd.DataFrame(df.groupby(['reviewed_by_id', 'unit_id', 'course_id']).size())
    student_unit_data.reset_index(inplace=True)
    student_unit_data.rename(columns={0: 'num_of_reviews'}, inplace=True)

    # student-course unique values
    unique_students_courses = student_unit_data.drop_duplicates(['reviewed_by_id', 'course_id'])
    unique_students_courses.rename(columns={'reviewed_by_id': 'user_id'}, inplace=True)
    unique_students_courses.drop(['unit_id', 'num_of_reviews'], axis=1, inplace=True)


    def calculate_pct_extra_revs(student_row, df):
        # student id
        student_id = student_row.iat[0]
        course_id = student_row.iat[1]

        # filter df to contain only students slice
        df = df[(df['reviewed_by_id'] == student_id) & (df['course_id'] == course_id)]

        total_units = len(df.unit_id.unique())
        num_units_with_extra_revs = len(df[df['num_of_reviews'] > 5].unit_id.unique())
        output = pd.Series({'user_id': student_id, 'total_units': total_units, 'extra_revs': num_units_with_extra_revs,
                        'pct_extras': num_units_with_extra_revs/total_units*100, 'course_id':course_id})

        return output

    student_extra_reviews = unique_students_courses.apply(calculate_pct_extra_revs, axis=1, args=(student_unit_data,))

    student_extra_reviews.sort_values(['pct_extras'], inplace=True, ascending=False)
    return student_extra_reviews

lala = return_num_of_additional_revs()
lala.to_csv('data/additional_reviews.csv')
print(lala )
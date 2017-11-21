import pandas as pd
import matplotlib.pyplot as plt
from Helpers.sqlAlchemy import get_smth
joined_unit = pd.read_csv('data/logs_with_course-all_labels.csv')
#joined_unit = joined_unit[joined_unit['probably_valid'] == True]

print(joined_unit.spent_time_seconds.describe())


enrollment = get_smth('SELECT user_id, course_id, role FROM diplomkatest.enrollment')
enrollment = enrollment[enrollment['role'] == 'student']
enrollment.drop(['role'], axis=1, inplace=True)
enrollment['user_course_id'] = enrollment['user_id'].astype(str) + "_" + enrollment['course_id'].astype(str)

# vlastně vyfiltruji nestudenty
joined_unit = pd.merge(joined_unit, enrollment, on='user_course_id')
print(joined_unit.spent_time_seconds.describe())

nit = joined_unit[joined_unit['spent_time_seconds'] <= 25000]
joined_unit = joined_unit[joined_unit['spent_time_seconds'] > 180]
joined_unit = joined_unit[joined_unit['spent_time_seconds'] <= 10000]
print(joined_unit.spent_time_seconds.describe())
joined_unit.spent_time_seconds.plot.hist(bins=25)
plt.show()

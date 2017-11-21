from __future__ import print_function
#import logy_go
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import linear_model
import tensorflow as tf
from mpl_toolkits.mplot3d import Axes3D

from Helpers.sqlAlchemy import get_smth

desired_width = 320
pd.set_option('display.width', desired_width)

def recode_time_spent(df):
    std = df['time_spent_seconds'].std()
    df.loc[df['time_spent_seconds'] <= 2 * std, 'time_spent_recoded'] = 2
    df.loc[df['time_spent_seconds'] <= std,'time_spent_recoded'] = 1
    df.loc[df['time_spent_seconds'] > 2 * std, 'time_spent_recoded'] = 3
    return df


def recode_actions(df):
    std = df['num_of_actions'].std()
    df.loc[df['num_of_actions'] <= 2 * std, 'num_of_actions_recoded'] = 2
    df.loc[df['num_of_actions'] <= std, 'num_of_actions_recoded'] = 1
    df.loc[df['num_of_actions'] > 2 * std, 'num_of_actions_recoded'] = 3
    return df


def student_unit_view():
    '''
    student_course = get_user_course_info.get_user_course_unit_info()
    student_course['user_unit_id'] = student_course['user_id_x'].astype(str) + "_" + student_course['unit_id_x'].astype(str)

    #student_course.to_csv('student')
    log_info = logy_go.get_user_unit_stats()


    joined = pd.merge(log_info, student_course, how='outer', left_on='user_unit', right_on='user_unit_id')
    print(joined)
    joined.to_csv('student_unit.csv')'''


    joined = pd.read_csv('logy_student_unit.csv', encoding='windows-1250')
    joined.dropna(inplace=True)
    joined.drop(['Unnamed: 0','user_id_x_y', 'unit_id_x', 'unit_id_y', 'user_id_y', 'user_unit_id'], axis=1, inplace=True)

    joined = joined[
        (joined['course_id'] == 2) | (joined['course_id'] == 4) | (joined['course_id'] == 5)]
    #joined = joined[joined['probably_valid'] == True]
    joined = joined[joined['user_id_x_x'] != 4]
    joined = joined[joined['course_id']!=2]
    joined['time_spent_seconds'] = pd.to_timedelta(joined['time_diff']).dt.seconds

    joined = recode_time_spent(joined)
    joined = recode_actions(joined)
    #joined = joined[joined['probably_valid'] == True]
    return joined
    print(joined.describe())
    print(joined.corr())



def analyze_by_user_course(final_logs_with_labels):


    def calc_student_course_investment(user_course_slice):
        # print(user_course_slice)

        vals = pd.Series({'total_actions': sum(user_course_slice['num_of_actions']),
                          'total_time_spent': sum(user_course_slice['spent_time_2']),
                          'avg_time_spent': np.mean(user_course_slice['spent_time_2'])
                          })
        return vals


    total_user_log_course_info = pd.DataFrame(final_logs_with_labels.groupby('user_course_id')
                                              .apply(calc_student_course_investment)).reset_index()
    #total_user_log_course_info = total_user_log_course_info[total_user_log_course_info['total_time_spent'] >= 120]

    #nvm[['user_id', 'course_id']] = nvm['user_course_id'].str.split('_', expand=True)

    enrollment = get_smth('SELECT user_id, course_id, role FROM diplomkatest.enrollment')
    enrollment = enrollment[enrollment['role'] == 'student']
    enrollment.drop(['role'], axis=1, inplace=True)
    enrollment['user_course_id'] = enrollment['user_id'].astype(str) + "_" + enrollment['course_id'].astype(str)

    total_user_log_course_info = pd.merge(total_user_log_course_info, enrollment, on='user_course_id')


    wtf = pd.read_csv('data/student_course-classific_score_slope.csv')
    wtf['user_course_id'] = wtf['user_id'].astype(str) \
                                                       + "_" + wtf['course_id_x'].astype(str)

    super_joined = pd.merge(total_user_log_course_info, wtf, on='user_course_id')


    print(super_joined.columns)
    for_analysis = super_joined.drop(['course_id_x', 'user_id_y', 'Unnamed: 0',
                       'should_have_points', 'achieved_minimum_points', 'point_distance', 'based_on_wo_nans',
                       'based_on_with_nans', 'user_id_x', 'course_id',
                                      'should_have_num_sols', 'slope_with_nans', 'slope_wo_nans',
                                      'avg_course_score_weighted', 'unit_count', 'pocet_ukolu', 'avg_time_spent'], axis=1)
    for_analysis['overkill'] = for_analysis['avg_score_classification'] + "_" + for_analysis['classification_based_on_assignements']
    print(for_analysis.columns)
    for_analysis.rename(columns={'pocet_bodu':'total_points', 'total_time_spent':'system_spent_time','avg_score':'avg_points'
                                 },inplace=True)

    import seaborn as sns

    f, ax = plt.subplots(figsize=(10, 8))
    corr = for_analysis.corr()
    sns.heatmap(corr, mask=np.zeros_like(corr, dtype=np.bool), cmap=sns.diverging_palette(220, 10, as_cmap=True),
                square=True, ax=ax, annot=True)


    print(for_analysis.corr())

    #print(for_analysis.groupby('avg_unit_time_spent_label').describe())
    for_analysis.groupby('avg_unit_time_spent_label').boxplot(column='avg_points')

    plt.show()
    return

    print(for_analysis.groupby('overkill').describe())

final_logs = pd.read_csv('data/logs_with_course-all_labels.csv')
final_logs['spent_time_2'] = pd.to_timedelta(final_logs.loc[:, "time_diff"])
final_logs['spent_time_2'] = final_logs['spent_time_2'].dt.total_seconds()


# dívám se jen na ty, kde vím, že mám všechny data
final_logs = final_logs[(final_logs['course_id_x'] == 2)|(final_logs['course_id_x'] == 4)|(final_logs['course_id_x'] == 5)]
final_logs = final_logs[(final_logs['course_id_x'] != 2)]

print("pocet unikátních uživatelů: ",len(final_logs.user_id_x.unique()))
print("pocet unikátních course-uživatelů: ",len(final_logs.user_course_id.unique()))



analyze_by_user_course(final_logs)
quit()
print(100*"-")
print("pohled dle unitů")
df_per_unit = student_unit_view()

X = df_per_unit[['num_of_actions','time_spent_seconds']]
y = df_per_unit['avg_score']



X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=7)

model = linear_model.LinearRegression()
model.fit(X_train, y_train)


print("rscore (unit view) is ", model.score(X_test,y_test))

quit()

# Parameters
learning_rate = 0.01
training_epochs = 100
display_step = 50

train_X = np.asarray(X_train['time_spent_seconds']).astype("float")
train_Y = np.asarray(y_train)

test_X = np.asarray(X_test['time_spent_seconds']).astype("float")
test_Y =np.asarray(y_test)


rng = np.random

n_samples = train_X.shape[0]

# tf Graph Input
X = tf.placeholder("float")
Y = tf.placeholder("float")

# Set model weights
W = tf.Variable(rng.randn(), name="weight")
b = tf.Variable(rng.randn(), name="bias")


# Construct a linear model
pred = tf.add(tf.multiply(X, W), b)

# Mean squared error
cost = tf.reduce_sum(tf.pow(pred-Y, 2))/(2*n_samples)
print(cost)
# Gradient descent
#  Note, minimize() knows to modify W and b because Variable objects are trainable=True by default
optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# Start training
with tf.Session() as sess:

    # Run the initializer
    sess.run(init)

    # Fit all training data
    for epoch in range(training_epochs):
        for (x, y) in zip(train_X, train_Y):

            sess.run(optimizer, feed_dict={X: x, Y: y})


        # Display logs per epoch step
        if (epoch+1) % display_step == 0:
            c = sess.run(cost, feed_dict={X: train_X, Y:train_Y})
            print({X: train_X, Y: train_Y})
            print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(c), \
                "W=", sess.run(W), "b=", sess.run(b))

    print("Optimization Finished!")
    training_cost = sess.run(cost, feed_dict={X: train_X, Y: train_Y})
    print("Training cost=", training_cost, "W=", sess.run(W), "b=", sess.run(b), '\n')

    # Graphic display
    plt.plot(train_X, train_Y, 'ro', label='Original data')
    plt.plot(train_X, sess.run(W) * train_X + sess.run(b), label='Fitted line')
    plt.legend()
    plt.show()

    # Testing example, as requested (Issue #2)
    #test_X = numpy.asarray([6.83, 4.668, 8.9, 7.91, 5.7, 8.7, 3.1, 2.1])
    #test_Y = numpy.asarray([1.84, 2.273, 3.2, 2.831, 2.92, 3.24, 1.35, 1.03])

    print("Testing... (Mean square loss Comparison)")
    testing_cost = sess.run(
        tf.reduce_sum(tf.pow(pred - Y, 2)) / (2 * test_X.shape[0]),
        feed_dict={X: test_X, Y: test_Y})  # same function as cost above
    print("Testing cost=", testing_cost)
    print("Absolute mean square loss difference:", abs(
        training_cost - testing_cost))

    plt.plot(test_X, test_Y, 'bo', label='Testing data')
    plt.plot(train_X, sess.run(W) * train_X + sess.run(b), label='Fitted line')
    plt.legend()
    plt.show()
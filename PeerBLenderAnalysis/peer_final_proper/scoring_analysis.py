import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib

from sklearn.preprocessing import minmax_scale, RobustScaler, StandardScaler

# snažilo se nějak dívat na reviews s pomocí těch mojich labelů - na prd
matplotlib.style.use('ggplot') # Look Pretty

df = pd.read_csv('joined.csv', encoding='windows-1250')

# only valid ones? zajímá mě solution is complete?
df = df[(df.status != "prep") & (df.solution_is_complete == 1)]

df['review_time_spent'] = pd.to_timedelta(pd.to_datetime(df.submitted_at) - pd.to_datetime(df.opened_at)).dt.seconds

# rychlá standardizace scoremodedistance
df.loc[df['score_mode_distance'].isnull(),'score_mode_distance'] = 0
df['score_distance_recoded'] = minmax_scale(df['score_mode_distance'].values.reshape(-1, 1), feature_range=(-1,-0.33)) * -1



def standardize_unique_words(df):
    joined = df
    joined['review_unique_num_of_words'].fillna(0, inplace=True)
    #graph of nonstandardized words
    #print(joined['review_unique_num_of_words'].describe())
    #nevim = joined['review_unique_num_of_words'].sort_values().reset_index(drop=True)
    #nevim.plot(kind="hist",legend=True, bins=40)
    #plt.show()

    # velke odchylky kazí distribuci -- nutno upravit, nemohu jen scaper - ukázat graf jen nascalovaných hodnot
    joined['review_unique_words_standardized'] = RobustScaler().fit_transform(joined['review_unique_num_of_words']
                                                                              .values.reshape(-1, 1))
    # super median --6
    joined.loc[joined['review_unique_words_standardized'] >= joined['review_unique_words_standardized'].quantile(0.9),
               'review_unique_words_standardized'] = 6
    # od 0.9 medián udělej min max od 1 do 5
    joined.loc[joined['review_unique_words_standardized'] <= joined['review_unique_words_standardized'].quantile(
        0.9), 'review_unique_words_standardized'] = \
        minmax_scale(joined.loc[joined['review_unique_words_standardized']
                                <= joined['review_unique_words_standardized'].quantile(0.9),
                                'review_unique_words_standardized'], (1, 5))
    # pro grafiky na psani
    print(joined['review_unique_words_standardized'].describe())

    print(joined['review_unique_words_standardized'].describe())
    nevim = joined['review_unique_words_standardized'].sort_values().reset_index(drop=True)
    nevim.plot(kind="hist",legend=True, bins=40)
    plt.show()

    determine_outliers = joined['review_unique_words_standardized'].sort_values().reset_index()
    determine_outliers.drop(['index'], axis=1, inplace=True)
    print(determine_outliers)
    return joined

standardize_unique_words(df)

def standardize_coef_values(df):


    quantil_75 = df.review_time_spent.quantile(q=0.75)
    relevant_rows = pd.DataFrame(df.loc[df['review_time_spent'] < quantil_75, 'review_time_spent']).reset_index()

    # hmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm?
    relevant_rows['time_standardized'] = minmax_scale(relevant_rows['review_time_spent'].values.reshape(-1, 1), feature_range=(0,2))

    print(relevant_rows)
    quit()
    # slicuji si kategorie a následně scaluji
    small = relevant_rows[relevant_rows['review_time_spent'] <= 100]
    mid = relevant_rows[(relevant_rows['review_time_spent'] >= 100) & (relevant_rows['review_time_spent'] <= 600) ]
    big = relevant_rows[relevant_rows['review_time_spent'] > 600]
    # standardize 0-3
    small['time_standardized'] = minmax_scale(small['review_time_spent'].values.reshape(-1, 1))
    mid['time_standardized'] = minmax_scale(mid['review_time_spent'].values.reshape(-1, 1)) + 1
    big['time_standardized'] = minmax_scale(big['review_time_spent'].values.reshape(-1, 1)) + 2
    valid_data = pd.concat([small, mid, big]).drop_duplicates()
    joined = df.merge(valid_data, how='left', left_index=True, right_on='index')
    joined['time_standardized'].fillna(1, inplace=True)

    print(joined.time_standardized.describe())
    # standardize num of unique words
    joined = standardize_unique_words(joined)

    return joined


standardized = standardize_coef_values(df)


def calculate_review_quality_koef(df):

    df['review_quality_coef'] = 1 * ~df['is_user_duplicate'] *\
                                (df['review_unique_words_standardized'] + df['time_standardized']) * df['score_distance_recoded']
    return df

calculate_review_quality_koef(standardized).to_csv('testing.csv')


quit()
my_labels = pd.read_excel('C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Skripty/python/peerStuff/review_label.xlsx',
                          sheetname='Sheet2')
# filtruj olabelovane
my_labels.dropna(inplace=True, subset=['My_label'])
# labely jsou na answerech --> pohled pres celé review
labels_review = pd.DataFrame(my_labels.groupby('id')['My_label'].mean()).reset_index()
# olabelovaný dataset bohužel nemá IDčka, ale řádky, tzn ID není id -- joinuji na index
joined = pd.merge(df, labels_review, how='left', left_on='Unnamed: 0' ,  right_on='id')


total_labeled = joined.dropna(subset=['My_label'])

# ok, zkusil jsem si nějak ML, nedává to bohužel smysl kvůli debilním labelům. Možná možná by ještě stálo za to zkusit nějaký clustering
total_labeled.drop(['id_x', 'solution_id', 'reviewed_by_id', 'opened_at', 'status', 'solution_is_complete',
                    'assessment', 'notes', 'id_y', 'submitted_at', 'Unnamed: 0'], axis=1, inplace=True)

# pod9v8m se na to přes reviews
total_labeled.drop(['answer_num_of_words', 'answer_answer_len', 'answer_unique_num_of_words', 'answer_review_len'],
                   axis=1, inplace=True)

# pro hodnoceni asi zbytečnost
total_labeled.drop(['mode_value', 'mode_occurrence', 'kolik_proc_je_jinak', 'review_status','is_diff_score',
                    'score_mode_distance', 'is_user_duplicate', 'num_of_revs', 'review_answer_len', 'review_num_of_words'], axis=1, inplace=True)
total_labeled.reset_index(inplace=True)
total_labeled.drop(['index'], axis=1, inplace=True)
print(total_labeled.columns)

X = total_labeled[['score', 'review_unique_num_of_words', 'review_review_len']]
y = total_labeled['My_label']

print(X)
print(y)

from sklearn import preprocessing
le = preprocessing.LabelEncoder()
y = le.fit_transform(y)




from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=7, test_size=0.3)

from sklearn import linear_model
model = linear_model.LinearRegression()
def drawLine(model, X_test, y_test, title):
  # This convenience method will take care of plotting your
  # test observations, comparing them to the regression line,
  # and displaying the R2 coefficient
  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.scatter(X_test, y_test, c='g', marker='o')
  ax.plot(X_test, model.predict(X_test), color='orange', linewidth=1, alpha=0.7)
  ax.scatter(X_test, y_test, c='g', marker='o')
  print ("Est 2014 " + title + " Life Expectancy: ", model.predict([[2014]])[0])
  print ("Est 2030 " + title + " Life Expectancy: ", model.predict([[2030]])[0])
  print ("Est 2045 " + title + " Life Expectancy: ", model.predict([[2045]])[0])

  score = model.score(X_test, y_test)
  title += " R2: " + str(score)
  ax.set_title(title)
model.fit(X_train,y_train)
print(model.score(X_test,y_test))



from sklearn import tree
model = tree.DecisionTreeClassifier(max_depth=9, criterion="entropy")
model.fit(X_train,y_train)

print(model.score(X_test,y_test))



from sklearn.svm import SVC

svc = SVC()
svc.fit(X_train,y_train)
print(svc.score(X_test,y_test))
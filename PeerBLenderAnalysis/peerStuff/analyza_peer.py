import pandas as pd

from Helpers.sqlAlchemy import get_smth

peer_info = pd.read_csv('peer_review_info.csv')

time_spent_info = pd.read_csv('timeUserRevSpent.csv')

reviews =  get_smth("SELECT * FROM review")

reviews.drop(['notes', 'assessment', 'status', 'solution_is_complete','solution_id', 'reviewed_by_id'],axis=1, inplace=True)
reviews['dumb_timediff'] = pd.to_timedelta(reviews.submitted_at - reviews.opened_at).dt.seconds

joined = peer_info.merge(reviews,how='left', left_on='answer_rev_id', right_on='id')
print(joined.columns)
joined.drop(['id', 'answer_num_of_words', 'answer_answer_len', 'answer_unique_num_of_words',
             'answer_review_len', 'review_num_of_words', 'review_answer_len',
             'review_unique_num_of_words', 'answer_rev_id',
             'submitted_at', 'opened_at', 'Unnamed: 0' ], axis=1, inplace=True)
print(joined)
joined.dropna(inplace=True)
#joined['cum_sum'] = pd.to_timedelta(joined['cum_sum']).dt.seconds
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

kmeans = KMeans(n_clusters=5)
kmeans.fit(joined)
labels = kmeans.predict(joined)
centroids = kmeans.cluster_centers_

print(labels)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(xs = centroids[:, 0], ys = centroids[:, 1], zs = centroids[:, 2], c = 'r', marker = 'x', s = 100)

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.show()
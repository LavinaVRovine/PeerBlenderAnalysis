import pandas as pd
import json
from sqlAlchemy import get_smth
import numpy as np
import datetime
import unicodedata
import matplotlib.pyplot as plt

reviews = get_smth("SELECT * FROM review")

reviews['dumb_timediff'] = pd.to_timedelta(reviews.submitted_at - reviews.opened_at).dt.seconds

print(reviews.dumb_timediff.describe())
#reviews =

quantil_75 = reviews.dumb_timediff.quantile(q=0.75)


total_len = len(reviews)
non_extreme_reviews = reviews[reviews['dumb_timediff'] < quantil_75]

print('basic len is {}, final len is {}, which means that loss is {} and thats {}%'
      .format(total_len, len(non_extreme_reviews), total_len - len(non_extreme_reviews), 1 -(len(non_extreme_reviews)/total_len )))

print(non_extreme_reviews['dumb_timediff'].describe())

with_3 = non_extreme_reviews[(non_extreme_reviews['score'] == 3)]
plt.figure()
with_3.dumb_timediff.plot.hist(bins=33)

podelane = non_extreme_reviews[(non_extreme_reviews['dumb_timediff'] <= 100) & (non_extreme_reviews['score'] == 3)]
print(podelane)
plt.show()
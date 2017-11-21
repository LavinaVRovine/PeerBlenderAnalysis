import matplotlib.pyplot as plt
import pandas as pd

from Helpers.sqlAlchemy import get_smth


# returns DF containing only improper reviews
def return_improper_peer_reviews():
    # load data
    reviews_df = get_smth("SELECT * FROM review")

    #reviews_df = reviews_df[reviews_df['status'] != "prep"]
    # calculate time between create and submit - (almost) time spent

    reviews_df['review_time_spent'] = pd.to_timedelta(reviews_df.submitted_at - reviews_df.opened_at).dt.seconds

    # first exploratory analysis
    print(reviews_df.review_time_spent.describe())

    # calculate Q3
    quantil_75 = reviews_df.review_time_spent.quantile(q=0.75)
    total_len = len(reviews_df)

    # leave everything, which is smaller than Q3 -
    # which is 1948 and smaller-basically everythin over 30min is "messy data"
    non_extreme_reviews = reviews_df[reviews_df['review_time_spent'] < quantil_75]

    # just to know how many rows were filtered
    print('basic len is {}, final len is {}, which means that loss is {} and thats {}%'
          .format(total_len, len(non_extreme_reviews), total_len - len(non_extreme_reviews), 1 - 
                  (len(non_extreme_reviews)/total_len)))
    # second exploratory analysis
    print(non_extreme_reviews['review_time_spent'].describe())
    # consider only reviews wih score 3, because we want to identify improper reviews - maybe change later?
    with_3 = non_extreme_reviews[(non_extreme_reviews['score'] == 3)]
    # third exploratory analysis
    print(with_3.review_time_spent.describe())

    fig = plt.figure()
    with_3.review_time_spent.plot.hist(bins=20)
    #with_3.review_time_spent.plot.hist(bins=200)
    fig.text(0.5, 0.04, 'Seconds', ha='center')

    with_3[(with_3['review_time_spent'] <= 180)].to_csv("low_timespent_explore.csv")
    # these are labeled as improper = podělané/odbyté reviews
    improper_reviews = non_extreme_reviews[(non_extreme_reviews['review_time_spent'] <= 100)
                                           & (non_extreme_reviews['score'] == 3)]
    print(improper_reviews)
    plt.show()
    return improper_reviews

return_improper_peer_reviews()

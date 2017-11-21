import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

df = pd.read_csv('joined.csv', encoding='windows-1250')

df = df[df['is_user_duplicate']]

test = df.groupby('reviewed_by_id').size()

test.plot.hist(bins=27)
plt.show()
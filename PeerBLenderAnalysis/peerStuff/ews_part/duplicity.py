import pandas as pd
import json
from sqlAlchemy import get_smth
import numpy as np
import datetime
import unicodedata

df = get_smth("SELECT * FROM review")

# only valid ones? zajímá mě solution is complete?
df = df[(df.status != "prep") & (df.solution_is_complete == 1)]

# pro labelování - začátek s rubrikami
df = df[df['submitted_at'] >= datetime.date(2016, 10, 1)]

# expandne assessmenty na dataframe
ids = df['id'].to_frame()

expanded_df = df["assessment"].apply(lambda row: pd.Series(json.loads(row)))


# vlastně hodí nonnany do leva
def squeeze_nan(x):
    original_columns = x.index.tolist()

    squeezed = x.dropna()
    squeezed.index = [original_columns[n] for n in range(squeezed.count())]

    return squeezed.reindex(original_columns, fill_value=np.nan)


def replace_if_list(val):

    if type(val) is list:
        return np.nan
    else:
        return val


def odstran_diakritiku(row):


    line = row
    line = unicodedata.normalize('NFKD', line)

    output = ''
    for c in line:
        if not unicodedata.combining(c):
            output += c

    return output
# zaměním listy za nan - tzn vše co nejsou odpovědi jsou nana
expanded_df = expanded_df.applymap(replace_if_list)


only_reviews = expanded_df.apply(squeeze_nan, axis=1)

only_reviews = only_reviews.dropna(axis=1, how='all')


# takové to pivotování -> multiindex s id a odpověďmi
only_reviews = only_reviews.stack()

only_reviews = only_reviews.str.lower()
only_reviews = pd.DataFrame(only_reviews)
only_reviews.reset_index(inplace=True)
# vrátí pouze text, někde byly i určité hodnoty hodnocení
only_reviews = only_reviews[~only_reviews[0].astype(str).str.isdigit()]
only_reviews.dropna(inplace=True)
# joinování IDčka review
only_reviews = pd.merge(ids,only_reviews, left_index=True, right_on='level_0',how='inner')

# smaže čísla - nejdou do lower:)
only_reviews[0] = only_reviews[0].str.replace('\d*', '')

only_reviews[0] = only_reviews[0].apply(odstran_diakritiku)


# newline na mezeru
only_reviews[0] = only_reviews[0].str.replace('\\n', ' ')
only_reviews[0] = only_reviews[0].str.replace('\\t', ' ')
# hypertextové odkazy, ale nevezme všechny:(
only_reviews[0] = only_reviews[0].str.replace(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '')

# nealfanumerické znaky - smajlíky, tečky, whathaveyou
only_reviews[0] = only_reviews[0].str.replace('[^a-zA-Z\d\s:]', '')
only_reviews[0] = only_reviews[0].str.replace('[,]', ' ')
only_reviews[0] = only_reviews[0].str.replace('[:]', ' ')
only_reviews[0] = only_reviews[0].str.replace("\'", '')
only_reviews[0] = only_reviews[0].str.strip()

only_reviews[0] = only_reviews[0].astype(str)
only_reviews.rename(columns={ 'level_1': 'answer_index', 0: 'answer'}, inplace=True)

def user_duplicates(df):
    duplicated = df[df.duplicated(subset='answer', keep=False)]
    return duplicated

def concat_review_answers(series):

    total_answers = series.values
    total_answers = list(total_answers)
    total_answers = ' '.join(total_answers)
    return(total_answers)

# sloučí všechny odpovědi do jednoho stringu
review_concatenated = pd.DataFrame(only_reviews.groupby(['level_0'])['answer'].apply(concat_review_answers))
review_concatenated.reset_index(inplace=True)

joined = review_concatenated.merge(df,how='left',left_on='level_0',right_on='id')

# vrátí df duplicit usera
duplicit_dle_user = joined.groupby('reviewed_by_id').apply(user_duplicates)
duplicit_dle_user.reset_index(inplace=True, drop=True)


duplicit_dle_user['dumb_timediff'] = pd.to_timedelta(duplicit_dle_user.submitted_at - duplicit_dle_user.opened_at).dt.seconds

print(duplicit_dle_user)
quit()
duplicit_pocet = duplicit_dle_user.groupby('reviewed_by_id').size()
print(duplicit_pocet.sort_values())
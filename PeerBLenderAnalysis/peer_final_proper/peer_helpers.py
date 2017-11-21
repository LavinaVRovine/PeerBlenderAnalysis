import pandas as pd
import numpy as np
import unicodedata


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


def format_and_clear_peer_answers(only_reviews):
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
    only_reviews.rename(columns={'level_1': 'answer_index', 0: 'answer'}, inplace=True)
    return only_reviews


def concat_review_answers(series):

    total_answers = series.values
    total_answers = list(total_answers)
    total_answers = ' '.join(total_answers)
    return total_answers


def reformat_peer_df(expanded_assessment_df, ids):
    expanded_assessment_df = expanded_assessment_df.applymap(replace_if_list)

    only_reviews = expanded_assessment_df.apply(squeeze_nan, axis=1)
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
    only_reviews = pd.merge(ids, only_reviews, left_index=True, right_on='level_0', how='inner')

    return only_reviews

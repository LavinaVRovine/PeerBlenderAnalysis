import pandas as pd
import numpy as np
from sqlAlchemy import get_smth


df = get_smth('select * from review')
# only valid ones? zajímá mě solution is complete?
df = df[(df.status != "prep") & (df.solution_is_complete == 1)]

def calc_note_frequency(df):

    user_review_count = len(df)
    # mazání prázdných
    only_with_notes = df[df['notes'] != ""]
    only_with_notes = only_with_notes[~only_with_notes['notes'].isnull()]

    user_num_of_notes = len(only_with_notes)
    note_frequency = user_num_of_notes / user_review_count * 100
    output = pd.Series({'user_num_of_notes': user_num_of_notes, 'user_review_count': user_review_count,
                       'pct_note_frequency' : note_frequency})
    return output


nvm = df.groupby(['reviewed_by_id']).apply(calc_note_frequency)

nvm.sort_values('pct_note_frequency', inplace=True, ascending=False)

print(nvm)

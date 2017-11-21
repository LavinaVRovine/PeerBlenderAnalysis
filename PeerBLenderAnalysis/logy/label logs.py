import pandas as pd

from Helpers.sqlAlchemy import get_smth

desired_width = 320
pd.set_option('display.width', desired_width)

# for log labeling
#sol_rev = get_smth('SELECT SOL.id as sol_id, SOL.unit_id as unit_id, RE.id as rev_id FROM diplomkatest.solution AS SOL LEFT JOIN diplomkatest.review AS RE ON SOL.id = RE.solution_id ')
with open("C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Skripty/solution_review_course_ids.sql", encoding='utf-8') as file:
    sql_statement = file.read()
sol_rev = get_smth(sql_statement)

# connect to data
df = pd.read_csv("C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Data_od_Honzy_Martinka/log.csv.gz",
                 compression='gzip', sep="\t")
# první řádek je fail
df.drop([0], inplace=True)
df.dropna(axis=1, inplace=True)

# change to datetime from str
df["log_date_time"] = pd.to_datetime(df.loc[:, "logged_at"])

# time vars
def label_log(log_row, sol_rev):
    if log_row['action'] == 'open':
        return log_row['entity_identifier']
    elif log_row['action'] == 'login':
        return None
    elif log_row['entity_name'] == 'Solution':
        relevant_row = sol_rev.loc[sol_rev['sol_id'] == log_row['entity_identifier'], 'unit_id']
        rel_row_unique = relevant_row.unique()
        if len(rel_row_unique) == 0:
            return None
        else:
            return rel_row_unique[0]
    elif  log_row['entity_name'] == 'Solution':
        relevant_row = sol_rev.loc[sol_rev['rev_id'] == log_row['entity_identifier'], 'unit_id']
        rel_row_unique = relevant_row.unique()
        if len(rel_row_unique) == 0:
            return None
        else:
            return rel_row_unique[0]
    else:
        return None



df['corresponding_unit'] = df.apply(label_log, args=(sol_rev,), axis=1)
# pokud se logne, tak nevím, ale on někam jde - určení z toho kam jde
df['corresponding_unit'].fillna(method='bfill', inplace=True)
#poslední řádek se neBfillne, fail....
df['corresponding_unit'].fillna(method='ffill', inplace=True)
df['corresponding_unit'] = df['corresponding_unit'].astype(int)

df = df.merge(sol_rev, how='left', left_on='corresponding_unit', right_on='unit_id')
df.drop(['sol_id', 'unit_id', 'rev_id'], axis=1, inplace=True)
# není třeba, pokud budu mít všechna data
df['course_id'].fillna(method='ffill', inplace=True)

df.to_csv('labeled_logs.csv',index=False)
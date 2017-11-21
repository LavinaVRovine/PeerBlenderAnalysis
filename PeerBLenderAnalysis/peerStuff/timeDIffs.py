import pandas as pd

from Helpers.sqlAlchemy import get_smth

reviews_df = get_smth("SELECT * FROM review")

# only valid ones? zajímá mě solution is complete?
reviews_df = reviews_df[(reviews_df.status != "prep") & (reviews_df.solution_is_complete == 1)]
# okey, toto nejde dělat - nutno prostě jí přes logy
'''
df["time_spent_reviewing"] = df["submitted_at"]- df["opened_at"]
print(len(df))
df = df[df['reviewed_by_id'] == 23]
df = df[df['time_spent_reviewing'] > pd.Timedelta('0 days 01:00:00')]
'''
# connect to data
logy = pd.read_csv("C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Data_od_Honzy_Martinka/log.csv.gz",
                 compression='gzip', sep="\t")

solution_ids = get_smth("SELECT solution.id, unit_id FROM solution")

def calculate_time_spent_review(row, logs, solution_ids):
    # najdi v logu část mezi review create and review submit
    # current reviewer only

    solution_id = row["solution_id"]
    # unit, ke kterému patří dané solution
    #unit_id = get_unit_id_of_sotution(solution_id)

    unit_id = solution_ids['unit_id'][solution_ids['id'] == solution_id].iat[0]

    reviewed_by = row.loc["reviewed_by_id"]
    review_id = row.loc["id"]
    logs = logs[logs["user_id"] == reviewed_by]

    review_slice = logs[(logs['entity_name'] == "Review") & (logs['entity_identifier'] == review_id )]
    # nevím, možná konec, prostě se sere
    if len(review_slice) <= 1:
        return None

    #počet řádků pro daný review - ideál 2 - create+submit. Více znamená, že updatoval review, tzn více submitu
    row["uhm"] = len(review_slice)

    # aktuálně jsem si řekl, že mě updaty nezajímají.....takže pouze 0 a 1-crate a first submit
    create = review_slice.iat[0,0]
    first_submit = review_slice.iat[1, 0]

    # df, která obsahuje všechny uživatelovi akce, které udělal od create po first submit
    relevant_logs = logs[(logs["id"] >= create) & (logs["id"] <= first_submit)]
    relevant_logs['logged_at'] = pd.to_datetime(relevant_logs.loc[:, "logged_at"])
    relevant_logs['time_diff'] = relevant_logs['logged_at'].diff()

    #on mohl mezi tím udělat spoustu debilních kroků, protože bůhvíco;
    # vidím dvě možnosti filtrování - buď pouze ty, kde je create a submit hned za sebou - nejvíc strict, nejvíc exact
    # nebo pouze odpovídající unit bez solutionu a podobně - méně exact, více dat:D
    # test druhé možnosti
    relevant_logs = relevant_logs[(relevant_logs["entity_name"] == 'Review') |
                                  ((relevant_logs['entity_identifier'] == unit_id) &
                                   (relevant_logs['entity_name'] == "Unit"))]



    # v podstatě vyfiltruj velkou časovou neaktivitu - 1h; budou rozdílné lognutí v jiné dny...
    relevant_logs = relevant_logs[relevant_logs["time_diff"] <= pd.Timedelta('0 days 01:00:00')]
    relevant_logs['cum_sum'] =  relevant_logs["time_diff"].cumsum()
    relevant_logs.drop(['entity_name', 'time_diff', 'logged_at', 'action'], axis=1, inplace=True)

    relevant_logs['solution_id'] = solution_id
    relevant_logs['corresponding_unit_id'] = unit_id

    if len(relevant_logs) != 0:
        # posl řádek, obsahuje výsledný čas
        last_row = relevant_logs.iloc[-1, :]
        return last_row

    else:
        return None

#df = df.iloc[4342:, :]
nevim = reviews_df.apply(calculate_time_spent_review, axis = 1, args=(logy, solution_ids))
#print("ahoj")


nevim.to_csv("timeUserRevSpent.csv")
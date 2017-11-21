import pandas as pd


# connect to data
df = pd.read_csv("C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Data_od_Honzy_Martinka/log.csv.gz",
                 compression='gzip', sep="\t")


df = df[(df['action'] == 'open') & (df['entity_name'] == "Unit")]

df["log_date_time"] = pd.to_datetime(df.loc[:, "logged_at"])

df['week_day'] = df["log_date_time"].dt.dayofweek + 1
# nevím, co je za week - cal? kdy začíná!?
df["year_week"] = df["log_date_time"].dt.year.astype(str) + \
                         "_" + df["log_date_time"].dt.week.astype(str)

test = df.groupby(["user_id", "year_week"]).count()
test.reset_index(inplace=True)
print(test)
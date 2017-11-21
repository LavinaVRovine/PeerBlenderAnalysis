import pandas as pd

# connect to data
df = pd.read_csv("C:/Users/pavel/Disk Google/Skola/Diplomka NEW/Data_od_Honzy_Martinka/log.csv.gz",
                 compression='gzip', sep="\t")

jen_loginy = df[df["action"] == "login"]
jen_loginy["log_date_time"] = pd.to_datetime(jen_loginy.loc[:, "logged_at"])

# nevím, co je za week - cal? kdy začíná!?
jen_loginy["year_week"] = jen_loginy["log_date_time"].dt.year.astype(str) + \
                         "_" + jen_loginy["log_date_time"].dt.week.astype(str)

jen_loginy["date"] = jen_loginy["log_date_time"].dt.date.astype(str)

# někde by se asi mělo brát, ale prozatím takhle
# potřebuji vědět všechny měsíce, ve kterých se uživatel MĚL lognout
unique_yearweeks = jen_loginy["year_week"].unique().tolist()


# umožňuje vypočítat které týdny se student do systému lognul
def calc_num_of_yw_logins(unique_year_weeks, df_slice):
    yw_logins = {}
    for x in unique_year_weeks:
        num_of_logins = df_slice.year_week[df_slice.year_week == x].count()
        yw_logins[x] = num_of_logins
    return yw_logins


# faster
kdosi_cosi = jen_loginy[jen_loginy["user_id"] == 234]

yw_num_of_logins = calc_num_of_yw_logins(unique_yearweeks, kdosi_cosi)
print(yw_num_of_logins)
quit()

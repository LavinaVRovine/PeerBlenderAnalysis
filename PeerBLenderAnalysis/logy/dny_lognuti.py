import pandas as pd

# umožňuje vypočítat které dny v týdnu se student do systému nejčastěji loguje
def calc_pct_of_weekday_logins(df_slice):
    total_logins = len(df_slice)
    yw_logins = {}
    for x in range(1, 8):
        num_of_logins = df_slice.week_day[df_slice.week_day == x].count()
        yw_logins[x] = round((num_of_logins / total_logins) * 100, 2)
    return yw_logins


def days_of_week_logged(user_slice):
    """
    :param user_slice = user_yearweek - slice - logins only
    :returns series with IDs, number of logins and days user logged into the system
    """
    num_of_logins = len(user_slice)
    days_logged = user_slice['week_day'].unique()
    user_id = user_slice['user_id'].unique()[0]
    year_week = user_slice['year_week'].unique()[0]

    return pd.Series({'user_id': user_id, 'year_week': year_week, 'logged_these_days': days_logged,
                      'num_of_logins': num_of_logins})


def num_of_actions(user_slice):
    """počítá celkový počet akcí v systému (countrows())
    :param user_slice  = yearweek slice - all logs
    :returns series with IDs, total number of actions and dict of dayOfTheWeek: actions
    """

    num_of_actions = len(user_slice)
    user_id = user_slice['user_id'].unique()[0]
    year_week = user_slice['year_week'].unique()[0]
    days_logged = user_slice['week_day'].unique()

    day_and_actions = {}
    for day in days_logged:
        day_slice = user_slice[user_slice['week_day'] == day]
        day_and_actions[day] = len(day_slice)

    return pd.Series(
        {'user_id': user_id, 'year_week': year_week, 'num_of_actions': num_of_actions, 'day_logins': day_and_actions})


def get_actions_and_logins(logs):
    """main function for actions and logins
    calculates number of logins and actions (countrows()) for student yeaweak
    :param logs = preprocessed logs
    :returns df
    """
    df = logs
    jen_loginy = df[df["action"] == "login"]

    weekday_logins = pd.DataFrame(jen_loginy.groupby(['user_id', 'year_week']).
                                  apply(days_of_week_logged)).reset_index(drop=True)
    weekday_logins['user_yw'] = weekday_logins['user_id'].astype(str) + "_" + weekday_logins['year_week']

    total_actions = pd.DataFrame(df.groupby(['user_id', 'year_week']).apply(num_of_actions)).reset_index(drop=True)
    total_actions['user_yw'] = total_actions['user_id'].astype(str) + "_" + total_actions['year_week']

    joined = pd.merge(total_actions, weekday_logins, how='left', left_on='user_yw', right_on='user_yw')

    joined['probably_valid'] = True
    # kdo má více jak 557 - je error díky chatu....recoduji na median
    joined.loc[joined['num_of_actions'] >= joined['num_of_actions'].quantile(q=0.9), 'probably_valid'] \
        = False
    joined.loc[joined['num_of_actions'] >= joined['num_of_actions'].quantile(q=0.9), 'num_of_actions'] \
        = joined['num_of_actions'].quantile(q=0.5)
    return joined

def get_actions_for_units(labeled_logs):
    """calculatets number of actions (countROws()) gouped by user and unit
    :param labeled_logs = labeled logs df
    :returns user/unit df with num of actions
    """
    labeled_logs = labeled_logs.groupby(['user_id', 'corresponding_unit']).size()
    unit_time_spent = pd.DataFrame(labeled_logs)
    unit_time_spent.reset_index(inplace=True)
    unit_time_spent.rename(columns={0:'num_of_actions'},inplace=True)
    unit_time_spent['probably_valid'] = True
    # kdo má více jak 557 - je error díky chatu....recoduji na median
    unit_time_spent.loc[unit_time_spent['num_of_actions'] >= unit_time_spent['num_of_actions'].quantile(q=0.9), 'probably_valid'] \
        = False
    unit_time_spent.loc[unit_time_spent['num_of_actions'] >= unit_time_spent['num_of_actions'].quantile(q=0.9), 'num_of_actions'] \
        = unit_time_spent['num_of_actions'].quantile(q=0.5)

    return unit_time_spent
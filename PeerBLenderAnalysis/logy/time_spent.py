import pandas as pd


def is_prev_value_equal_current(action_series):
    """check wgether login is preceded by logout, if so, return false - should'ne be considered

    :param action_series = series of actions for user
    :returns series - true/false
    """

    action_series[(action_series == 'login') & (action_series.shift(-1) == 'logout')] = False
    action_series[action_series != False] = True

    return action_series


def calculate_time_spent(logs):
    """main function for calculating time spent per user year week
    :param logs = preprocessed logs
    :returns df
    """

    df = logs
    df['time_diff'] = df.groupby(["user_id"])["log_date_time"].diff()
    # počítá, zdali logout předchází login pro jednotlivé usery - když ano, tak by se daná hodnota neměla brat
    df["should_be_considered"] = df.groupby(["user_id"])["action"].apply(is_prev_value_equal_current)
    df = df[df["should_be_considered"] == True]

    df = df[df['time_diff'] <= pd.Timedelta('0 days 0:30:00')]

    time_spent = df.groupby(['user_id', 'year_week'])['time_diff'].sum()
    time_spent = pd.DataFrame(time_spent)
    time_spent.reset_index(inplace=True)
    time_spent['user_yw'] = time_spent['user_id'].astype(str) + "_" + time_spent['year_week']
    return time_spent


def calculate_time_spent_by_unit(labeled_logs):
    """main function for calculating time spent per user year week
    :param logs = preprocessed logs
    :returns df
    """

    df = labeled_logs
    df['time_diff'] = df.groupby(["user_id"])["log_date_time"].diff()
    # počítá, zdali logout předchází login pro jednotlivé usery - když ano, tak by se daná hodnota neměla brat
    df["should_be_considered"] = df.groupby(["user_id"])["action"].apply(is_prev_value_equal_current)
    df = df[df["should_be_considered"] == True]

    df = df[df['time_diff'] <= pd.Timedelta('0 days 0:30:00')]

    unit_time_spent = df.groupby(['user_id', 'corresponding_unit'])['time_diff'].sum()
    unit_time_spent = pd.DataFrame(unit_time_spent)
    unit_time_spent.reset_index(inplace=True)

    return unit_time_spent


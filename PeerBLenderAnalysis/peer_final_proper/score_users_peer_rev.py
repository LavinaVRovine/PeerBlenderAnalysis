import pandas as pd
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv('testing.csv', encoding='windows-1250')


def punish_big_score_mode_distance(df):
    #df['review_score_with_mode_distance_considered'] = df['review_quality_coef']
    df['mode_difference_punish_coef'] = 1
    minMax = MinMaxScaler((-0.75, -0.25))
    # měl bych brát jen ty, které nejsou sporné, aneb se shodlo hodně lidí - asi 4/5 - nutno relabelovat...

    # koeficient toho, jak moc se vzdálil od mode hodnoty punishuje score od 0.25 do 0.75 =  vzdálil se málo, vynásob
    #0.75, vzdálil se moc (3) vynásob 0.25
    df.loc[(df['review_status'] == 'alright') & (df['score_mode_distance'] >= 1), 'mode_difference_punish_coef'] \
        = abs(minMax.fit_transform(df.loc[(df['review_status'] == 'alright') & (df['score_mode_distance'] >= 1),
           'score_mode_distance'].values.reshape(-1,1)))

    df['score_with_mode_difference_punish'] = df['review_quality_coef'] * df['mode_difference_punish_coef']

    return df



df = punish_big_score_mode_distance(df)

test = df.groupby('reviewed_by_id')['score_with_mode_difference_punish'].mean()
print(test.sort_values())
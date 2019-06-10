import pandas as pd
import numpy as np

from sazonal_consumption import final_df
from CONSUMPTION_FUNC import df_original

def cons_func(money):

    profile = {'Type': 'One Student',
               'Month Bill': 5,
               'Bill': money}

    Price_kWh = 0.2284

    kWh_month = profile['Bill'] / Price_kWh

    profile_df = final_df * kWh_month / 30

    x = np.array(profile_df)
    y = np.array(df_original.loc[:, 'Watts'])

    y.shape = (24, 1)
    x.shape = (1, 12)

    z = np.dot(y, x)

    return z


def consumption(money):

    native_times = pd.date_range(start='1999-01-01', end='2019-01-01', freq='1h')

    df_times = pd.DataFrame({'date': native_times})

    df_times['Hour'] = df_times['date'].dt.hour
    df_times['Month'] = df_times['date'].dt.month
    df_times["consum_kWh"] = np.nan

    del df_times['date']

    np_fin = [[]]

    z = cons_func(money)

    for i in range(0,24):

        for j in range(0, 12):

            df_times.loc[(df_times['Hour'] == i) & (df_times['Month'] == j+1), 'consum_kWh'] = z[i, j]

    consum_Wh = df_times['consum_kWh']*1000

    yearly_consum_Wh = consum_Wh.sum() / 20

    return consum_Wh, yearly_consum_Wh


import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

def fit_func(reader, order):

    x = reader.loc[:, 'month']
    y = reader.loc[:, 'consumption']

    n = order

    z = np.polyfit(x, y, n)

    p = np.poly1d(z)

    xp = np.linspace(1, 12)

    return p, xp

saz_reader = open('C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\CODE\\Google API\\sazonal_consumption_2.txt', 'rb')
saz_read = pd.read_csv(saz_reader, encoding='utf-8')
saz_reader.close()

x_list = saz_read.loc[:, 'month']
y_list = saz_read.loc[:, 'consumption']

top_mean = top_max = 999
k = 0
m = 0

for i in range(1,15):

    p_fitted, x_fitted = fit_func(saz_read, i)

    fitted_list = {}
    fitted_df = {}

    for j in range(len(x_list)):

        fitted_list[j] = p_fitted(x_list[j])


    fitted_df = pd.DataFrame({'Fitted_cons': fitted_list,
                              'Expected': y_list})

    error = fitted_df['Fitted_cons'] - fitted_df['Expected']

    error = error.describe()
    error_mean = error.loc['mean']
    error_max = error.loc['max']

    if error_mean < top_mean:

        top_mean = error_mean
        k = i

    if error_max < top_max:

        top_max = error_max
        m = i


p_final, x_final = fit_func(saz_read, k)

final_list = {}

for i in range(1,13):

    final_list[i] = p_final(i)

final_df = pd.DataFrame({'month': final_list})

mean_final = final_df.mean()['month']

final_df = final_df/mean_final
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sazonal_consumption import final_df

def plot_styling():

    plt.style.use('dark_background')

    plt.gca().yaxis.grid(True, color='gray')

    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Ubuntu Mono'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['xtick.labelsize'] = 8
    plt.rcParams['ytick.labelsize'] = 8
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 12

    for spine in plt.gca().spines.values():
        spine.set_visible(False)


    plt.title(f'Duck Curve Functon - Poligonal Regression Level {n}')
    plt.xlabel('Hour')
    plt.ylabel('Watts indicator [Adimensional]')

    plt.ylim((0, 30))
    plt.xlim(0,24)

csv_reader = open('C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\CODE\\Google API\\Consumption.txt', 'rb')
csv_read = pd.read_csv(csv_reader, encoding='latin1', header=None)
csv_reader.close()

for i in range(1, 16):

    plt.clf()

    x = csv_read.loc[:, 0]
    y = csv_read.loc[:, 1]

    n = i

    plot_styling()

    plt.plot([x], [y], marker='o', markersize=3)

    z = np.polyfit(x, y, n)

    p = np.poly1d(z)

    xp = np.linspace(x.min(), x.max())

    plt.plot(xp, p(xp), '-',
             color='mediumseagreen',
             alpha = 0.4,
             linewidth = 4,
             ls='-',
             label=f'Polinomial Regressor {n}',
             zorder=1)


    i = i+1

hours = {}
Watts_Ad = {}

for i in range(24):

    hours[i] = i
    Watts_Ad[i] = p(i)


df_original = pd.DataFrame({'Hour': hours,
                            'Watts': Watts_Ad})


mean_original = df_original["Watts"].mean()
mean_inverse = 1 / mean_original


sum_original = df_original["Watts"].sum()
sum_inverse = 1 / sum_original

df_original.loc[:,'Watts'] *= sum_inverse


profile = {'Type': 'One Student',
           'Month Bill': 5,
           'Bill': 100}

Price_kWh = 0.2284

kWh_month = profile['Bill'] / Price_kWh

profile_df = final_df * kWh_month / 30

x = np.array(profile_df)
y = np.array(df_original.loc[:,'Watts'])

y.shape = (24, 1)
x.shape = (1, 12)

z = np.dot(y, x)
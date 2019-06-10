import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model

def module_name_func(mod):

    part = mod.split('_')

    name = {}

    for i in range(len(part)):

        if part[i].isdigit():
            year_int = int(part[i])

            if 2000 <= year_int <= 2100:
                name[i] = year_int
                break

            else:
                name[i] = year_int

        else:
            name[i] = part[i]

    name_final = ''

    for i in range(len(name)):

        if name[i] == '':
            pass

        else:

            if i > 0:

                if name[i - 1] == ' ' and name[i] == ' ':
                    pass

                else:
                    name_final = f'{name_final} {name[i]}'

            else:

                name_final = f'{name_final} {name[i]}'

    return name_final


def searched_deco_func(panel):

    mod = module_name_func(panel).split(' ')

    array = re.findall(r'[0-9]+', module_name_func(panel))

    Power = {}

    for i in range(len(array)):

        tw = int(array[i])
        if 999 > tw > 30:

            try:
                Power = array[i]

            except:
                pass

    brand = mod[1]
    year = mod[len(mod) - 1]

    panel_nameinfo = {'Brand': brand, 'Year': year, 'Power': Power}

    panel_nameinfo = pd.Series(panel_nameinfo)

    factor = {}

    for i in range(2, len(mod)):

        factor[i - 2] = mod[i]
        i = i + 1

    factor = pd.Series(factor)
    panel_nameinfo = panel_nameinfo.append(factor)

    return panel_nameinfo


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



def plot_PowervsPrice(df, regr, ransac, x, W):

    plot_styling()

    df.plot(x='Power', y='Price', style='o')

    plt.title(f'{searched_brand} Power vs Price interpolation for {W}W')
    plt.xlabel('Power [W]')
    plt.ylabel('Price [$]')

    df_aux = df.describe()

    min_price = df_aux.loc['min']['Price']
    min_power = df_aux.loc['min']['Power']
    max_price = df_aux.loc['max']['Price']
    max_power = df_aux.loc['max']['Power']

    plt.ylim((min_price*0.5, max_price + min_price*0.5))
    plt.xlim((min_power * 0.5, max_power + min_power * 0.5))

    line_x = np.arange(min_power * 0.7, max_power + min_power * 0.3)[:, np.newaxis]
    line_y = regr.predict(line_x)
    line_y_ransac = ransac.predict(line_x)

    plt.plot(line_x, line_y_ransac,
             color='teal',
             alpha=0.4,
             linewidth=10,
             label='RANSAC Regressor',
             solid_capstyle = "round",
             zorder=0)

    i_x = W
    i_y = round(ransac.predict([[W]])[0][0], 2)

    plt.annotate(f'${i_y} for {i_x}W',
                 xy=(i_x, i_y),
                 arrowprops=dict(arrowstyle='->'),
                 xytext=(i_x * 0.7, i_y * 1))

    plt.plot(x, regr.predict(x),
             color='salmon',
             linewidth=2,
             ls='-',
             label='Linear Regressor',
             zorder=1)

    plt.legend(loc='upper left', frameon=False)

    plt.gca().axes.get_yaxis().set_visible(True)

    plt.savefig(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\CODE\\Plots\\{searched_brand}_{W}Watts_plot.png')


def interpolating(df, W):

    df = df.astype(float)

    length = len(df)

    x = df['Power'].values.reshape(length, 1)
    y = df['Price'].values.reshape(length, 1)

    regr = linear_model.LinearRegression()
    regr.fit(x, y)

    ransac = linear_model.RANSACRegressor()
    ransac.fit(x, y)
    inlier_mask = ransac.inlier_mask_
    outlier_mask = np.logical_not(inlier_mask)

    plot_PowervsPrice(df, regr, ransac, x, W)



def data_2():

    prices_reader = open('C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\CODE\\Google API\\prices_solar_2.csv', 'rb')
    prices_read = pd.read_csv(prices_reader, encoding='latin1')

    database_name = str(prices_reader).split("'")
    db_len = len(database_name)
    database_name = database_name[db_len - 2]
    database_name = database_name.split('\\')
    db_len = len(database_name)
    database_name = database_name[db_len - 1]

    prices_reader.close()

    j = 0

    searching_nameinfo = pd.DataFrame()

    for i in range(len(prices_read)):

        searching_brand_splited = prices_read.iloc[i][0].split(' ')[0]

        if searching_brand_splited == searched_brand.split(' ')[0]:

            df2 = {'Brand': prices_read.iloc[i][0],
                   'Model': prices_read.iloc[i][1],
                   'Price': prices_read.iloc[i][3],
                   'Size': prices_read.iloc[i][4],
                   'Power': prices_read.iloc[i][2],
                   'Weight': prices_read.iloc[i][5],
                   'Country': prices_read.iloc[i][6],
                   'Database': database_name}

            searching_nameinfo = searching_nameinfo.append(df2, ignore_index=True)

            j = j+1

        else:

            i = i+1

    return searching_nameinfo, j


def data_1():

    prices_reader = open('C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\CODE\\Google API\\prices.csv', 'rb')

    database_name = str(prices_reader).split("'")
    db_len = len(database_name)
    database_name = database_name[db_len - 2]
    database_name = database_name.split('\\')
    db_len = len(database_name)
    database_name = database_name[db_len - 1]

    prices_read = pd.read_csv(prices_reader, encoding='latin1')
    prices_reader.close()

    j = 0

    searching_nameinfo = pd.DataFrame()

    for i in range(len(prices_read)):

        searching_brand_splited = prices_read.iloc[i]['Brand'].split(' ')[0]

        if searching_brand_splited == searched_brand.split(' ')[0]:

            df2 = {'Brand': prices_read.iloc[i]['Brand'],
                   'Model': prices_read.iloc[i]['Solar Panel'],
                   'Price': prices_read.iloc[i]['$ per Panel'],
                   'Power': prices_read.iloc[i]['Factory'],
                   'Warranty': prices_read.iloc[i]['Warranty'],
                   'Country': prices_read.iloc[i]['Country'],
                   'Database': database_name}

            searching_nameinfo = searching_nameinfo.append(df2, ignore_index=True)

            j = j + 1

        else:

            i = i + 1

    return searching_nameinfo, j


def data_set(searched_brand):

    try:
        searching_nameinfo_2, j_2 = data_2()

    except:

        searching_nameinfo_2, j_2 = pd.DataFrame(), 0

    try:
        searching_nameinfo_1, j_1 = data_1()

    except:

        searching_nameinfo_1, j_1 = pd.DataFrame(), 0

    j = j_1 + j_2

    searching_nameinfo = searching_nameinfo_2.append(searching_nameinfo_1, sort=False, ignore_index=True)

    if j == 0:

        print(f'No modules from {searched_brand} in our database')

    Panels_Prices = pd.Series(searching_nameinfo.loc[: , "Price"])
    Panels_Power = pd.Series(searching_nameinfo.loc[: , "Power"])

    for i in range(len(Panels_Power)):

        if searching_nameinfo.iloc[i]['Database'] == 'prices_solar_2.csv':
            Panels_Power[i] = Panels_Power[i].split('W')[0]

    for i in range(len(Panels_Prices)):

        Panels_Prices[i] = Panels_Prices[i].split('$')[1]

    df = pd.DataFrame({'Price': Panels_Prices.values,
                       'Power': Panels_Power.values})


    return df


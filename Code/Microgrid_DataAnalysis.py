import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import os,random, math, pickle
import seaborn as sns

from datetime import datetime


def find_path():
    # Return DATA Folder Path

    data_path = sys.path[0].split('London_Project')[0]
    data_path = f'{data_path}\\DATA\\Smart meters in London\\Combined\\'

    return data_path


def csv_func(i):

    csv_reader = open(f'C:\\Users\\diogo\\Desktop\\perkier tech\\Energy\\Comunities\\consumer_{i}.csv', 'rb')
    csv_read = pd.read_csv(csv_reader, encoding='latin1')
    csv_reader.close()

    return csv_read


def see_all():
    # Alongate the view on DataFrames

    pd.set_option('display.max_rows', 1000)
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)


def reduce_mem_usage(df, verbose=True):

    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

    start_mem = df.memory_usage().sum() / 1024 ** 2

    for col in df.columns:

        col_type = df[col].dtypes

        if col_type in numerics:

                c_min = df[col].min()
                c_max = df[col].max()

                if str(col_type)[:3] == 'int':

                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)

                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)

                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)

                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)

                else:

                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)

                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)

                    else:
                        df[col] = df[col].astype(np.float64)

        end_mem = df.memory_usage().sum() / 1024**2

        if verbose:

            print('Mem. usage decreased from {:5.2f}Mb  to {:5.2f}Mb ({:.1f}% reduction)'.format(start_mem, end_mem, 100 * (start_mem - end_mem) / start_mem))

        return df, start_mem, end_mem


def plot_styling():

    # plt.style.use('dark_background')
    plt.style.use('seaborn-bright')

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

    # plt.tick_params(top='False', bottom='False', left='False', right='False', labelleft='False', labelbottom='True')

    for spine in plt.gca().spines.values():
        spine.set_visible(False)


def plot_titles(data):

    plt.title('Energy vs Time')

    plt.ylabel('Energy')
    plt.xlabel('Time [mins]')

    max_y = data.loc[:,'T_room'].max() + 0.15*(data.loc[:,'T_room'].max())
    max_x = data.loc[:,'Minutes'].max() + 0.15*(data.loc[:,'Minutes'].max())

    plt.ylim((-5, max_y))
    plt.xlim(0,max_x)

    plt.plot(data.loc[:, 'Minutes'], data.loc[:, 'T_room'],
             ',', markersize=3,
             label=f'Room Temperature',
             zorder=1)

    plt.plot(data.loc[:, 'Minutes'], data.loc[:, 'T_amb'],
             ',', markersize=1, alpha= 0.3,
             label=f'Amb. Temperature',
             zorder=3)

    plt.plot(data.loc[:, 'Minutes'], data.loc[:, 'Power']/6000, ',',
             markersize=10, alpha= 0.5, label= 'Power/6000')

    plt.legend(title='Legend:')
    plt.show()


def see_missing_data(df):

    total = df.isnull().sum().sort_values(ascending = False)
    percent = (df.isnull().sum()/df.isnull().count()*100).sort_values(ascending = False)

    missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])

    return missing_data


def correlation_plots(df):

    # plt.figure(figsize=(20, 8))

    sns.palplot(sns.color_palette("Paired"))

    # index_values = df.loc[:, 'NXP']
    # df.set_index('NXP', inplace=True, drop=True)

    sns.heatmap(df, annot=True, center=0, fmt='.1%')

    plt.title('Correlation Heatmap')
    plt.show()



def get_correlations(df):

    corrs = df.corr()

    print(corrs)

    correlation_plots(corrs)


def compare_test_train(df_test, df_train, column):
    # Create histograms to compare the test and train set

    fig, ax = plt.subplots(figsize=(10, 10))

    sns.distplot(df_train[column].dropna(), color='green', ax=ax).set_title(column, fontsize=16)
    sns.distplot(df_test[column].dropna(), color='purple', ax=ax).set_title(column, fontsize=16)

    plt.xlabel(column, fontsize=15)
    plt.legend(['train', 'test'])
    plt.show()


def group_data(df_1, df_2, group_by):

    pass


def separate_data(df_1):

    pass


def id_outliers(df):

    pass


def get_consumer_statistics(df):

    unique_cons = df.loc[:, 'Consumer'].unique()

    consumer_dict = {}
    total_bought = {}
    mean_bought = {}
    total_sold = {}
    mean_sold = {}
    batt_level = {}

    mean_total_bought = 0
    meantotal_sold = 0

    i = 0

    for consumer in unique_cons:

        unique_df = df.loc[df['Consumer'] == consumer].reset_index(drop=True)

        consumer_dict[i] = consumer

        total_bought[i] = unique_df.loc[:,'Bought[kW]'].sum()
        mean_bought[i] = unique_df.describe()['Bought[kW]'].loc['mean']
        total_sold[i] = unique_df.loc[:,'Sold[kW]'].sum()
        mean_sold[i] = unique_df.describe()['Sold[kW]'].loc['mean']

        mean_total_bought += total_bought[i]
        meantotal_sold += total_sold[i]

        i += 1

    consumer_dict[i] = 'Mean'
    total_bought[i] = mean_total_bought/(i)
    total_sold[i] = meantotal_sold/(i)


    statistics_df = pd.DataFrame({'Consumer': consumer_dict,
                                  'En_Bought[kWh]': total_bought,
                                  'En_Sold[kWh]': total_sold})


    print(statistics_df)

    quit()



def main():

    data_set = {}

    path = "C:\\Users\\diogo\\Desktop\\perkier tech\\Energy\\Comunities\\banking.csv"

    csv_reader = open(path, 'rb')
    csv_read = pd.read_csv(csv_reader, encoding='latin1')
    csv_reader.close()

    get_consumer_statistics(csv_read)

    print(csv_read.sort_values(by=['Batt_Level'], ascending=True).reset_index(drop=True))

    csv_read['Bought[kW]'].plot(figsize=(15, 5), color='firebrick')
    csv_read['Sold[kW]'].plot(figsize=(15, 5), color='lime')
    plt.show()
    plt.clf()

    quit()

    for i in range(1):

        data_set[i] = csv_func(i).set_index('Date')

        data_set[i]['Sold[kW]'].plot(figsize=(15, 5))


        # quit()

    plt.show()
    quit()
    print('\n'*5)


    # # Names of all databases given
    # data_names = ['test', 'weather_train', 'train', 'weather_test', 'sample_submission', 'building_metadata']
    # # data_names = ['weather_train', 'train', 'building_metadata']
    #
    # data_set = {}
    # i = 0
    #
    # for name in data_names:
    #
    #     data_set[i] = csv_func(f'{name}')
    #     i += 1
    #
    # for key, d in data_set[2].groupby('meter_reading'):
    #     break
    #     print(d.head())
    #
    # plot_styling()
    #
    # data_set[2]['meter_reading'].plot(figsize=(15, 5))
    #
    # plt.show()
    # print('\n')
    missing_data_df = {}

    for i in range(len(data_set)):

        print(f"{i}:")
        missing_data_df[i] = see_missing_data(data_set[i])
        print(missing_data_df[i])
        print('\n')

    # get_correlations(data_set[2])
    #
    # compare_test_train(data_set[3], data_set[1], 'air_temperature')



if __name__ == "__main__":

    plot_styling()
    see_all()
    main()

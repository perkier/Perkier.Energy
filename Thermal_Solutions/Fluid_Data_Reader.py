from CoolProp.CoolProp import PropsSI, PhaseSI, HAPropsSI
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import datetime


def find_path():
    # Return DATA Folder Path

    data_path = sys.path[0].split('CODE')[0]
    data_path = f'{data_path}\\Fluid_Selection\\Results\\'

    return data_path


def csv_func(name):

    name = f'{name}'

    csv_reader = open(f'{find_path()}{name}.csv', 'rb')
    csv_read = pd.read_csv(csv_reader, encoding='latin1')
    csv_reader.close()

    # csv_read = csv_read.sample(frac=1).reset_index(drop=True)

    return csv_read


def see_all():
    # Alongate the view on DataFrames

    pd.set_option('display.max_rows', 1000)
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)


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

    # plt.tick_params(top='False', bottom='False', left='False', right='False', labelleft='False', labelbottom='True')

    for spine in plt.gca().spines.values():
        spine.set_visible(False)


def plot_titles(data):

    plt.title('Temperature vs Time')

    plt.ylabel('Temperature [ºC]')
    plt.xlabel('Time [mins]')

    max_y = data.loc[:,'T_room'].max() + 0.15*(data.loc[:,'T_room'].max())
    max_x = data.loc[:,'Minutes'].max() + 0.15*(data.loc[:,'Minutes'].max())

    plt.ylim((-5, max_y))
    plt.xlim(0,max_x)

    plt.plot(data.loc[:, 'Minutes'], data.loc[:, 'T_room'],
             '.', markersize=1,
             label=f'Room Temperature',
             zorder=1)

    plt.plot(data.loc[:, 'Minutes'], data.loc[:, 'T_amb'],
             '.', markersize=1, alpha= 0.3,
             label=f'Amb. Temperature',
             zorder=3)

    plt.plot(data.loc[:, 'Minutes'], data.loc[:, 'Power']/6000, '.-',
             markersize=7, alpha= 0.3)

    plt.show()


def convert_time(df):

    new_time = {}

    df['Minutes'] = df.loc[:,'Time']

    for i in range(len(df)):

        new_time[i] = str(datetime.timedelta(minutes=int(df.iloc[i].loc['Time'])))

    new_dates = pd.Series(new_time)

    df['Time'] = new_dates

    return df


def main():

    see_all()

    temp_df = csv_func('R125')
    temp_df = convert_time(temp_df)

    plot_styling()
    plot_titles(temp_df)


if __name__ == '__main__':

    main()

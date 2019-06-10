import pandas as pd
import os

def modules(num):

    fatura_euro = f'{num}euro'

    csv_reader_1 = open(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\Porto\\{fatura_euro}__panels_1.csv', 'rb')
    csv_read_1 = pd.read_csv(csv_reader_1, encoding='latin1')
    csv_reader_1.close()

    csv_reader_0 = open(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\Porto\\{fatura_euro}__panels_0.csv', 'rb')
    csv_read_0 = pd.read_csv(csv_reader_0, encoding='latin1')
    csv_reader_0.close()

    csv_reader_m1 = open(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\Porto\\{fatura_euro}__panels_-1.csv', 'rb')
    csv_read_m1 = pd.read_csv(csv_reader_m1, encoding='latin1')
    csv_reader_m1.close()

    csv_read_0 = csv_read_0.dropna().sort_values(by='Recom_Panels_Savings', ascending=False).reset_index(drop=True)
    csv_read_1 = csv_read_1.dropna().sort_values(by='Recom_Panels_Savings', ascending=False).reset_index(drop=True)
    csv_read_m1 = csv_read_m1.dropna().sort_values(by='Recom_Panels_Savings', ascending=False).reset_index(drop=True)

    return csv_read_1, csv_read_0, csv_read_m1


def csv_func_precision(num):

    fatura_euro = f'{num}euro'

    csv_reader_1 = open(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\Porto\\precision\\{fatura_euro}__panels_1.csv', 'rb')
    csv_read_1 = pd.read_csv(csv_reader_1, encoding='latin1')
    csv_reader_1.close()

    csv_reader_0 = open(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\Porto\\precision\\{fatura_euro}__panels_0.csv', 'rb')
    csv_read_0 = pd.read_csv(csv_reader_0, encoding='latin1')
    csv_reader_0.close()

    csv_reader_m1 = open(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\Porto\\precision\\{fatura_euro}__panels_m1.csv', 'rb')
    csv_read_m1 = pd.read_csv(csv_reader_m1, encoding='latin1')
    csv_reader_m1.close()

    csv_read_0 = csv_read_0.dropna().sort_values(by='Savings_Precision', ascending=False).reset_index(drop=True)
    csv_read_1 = csv_read_1.dropna().sort_values(by='Savings_Precision', ascending=False).reset_index(drop=True)
    csv_read_m1 = csv_read_m1.dropna().sort_values(by='Savings_Precision', ascending=False).reset_index(drop=True)

    return csv_read_1, csv_read_0, csv_read_m1


def csv_func_batt(num, i):

    fatura_euro = f'{num}euro'

    csv_reader_1 = open(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\Porto\\precision\\Batteries\\{i}panel_{fatura_euro}__panels_1.csv', 'rb')
    csv_read_1 = pd.read_csv(csv_reader_1, encoding='latin1')
    csv_reader_1.close()

    csv_reader_0 = open(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\Porto\\precision\\Batteries\\{i}panel_{fatura_euro}__panels_0.csv', 'rb')
    csv_read_0 = pd.read_csv(csv_reader_0, encoding='latin1')
    csv_reader_0.close()

    csv_reader_m1 = open(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\Porto\\precision\\Batteries\\{i}panel_{fatura_euro}__panels_m1.csv', 'rb')
    csv_read_m1 = pd.read_csv(csv_reader_m1, encoding='latin1')
    csv_reader_m1.close()

    return csv_read_1, csv_read_0, csv_read_m1


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

for n in range(50, 65, 5):

    prec_read_1, prec_read_0, prec_read_m1 = csv_func_precision(n)

    bought_x_1 = {}
    bought_x_0 = {}
    bought_x_m1 = {}

    sold_x_1 = {}
    sold_x_0 = {}
    sold_x_m1 = {}

    Savings_Precision_wlosses_1 = {}
    Savings_Precision_wlosses_0 = {}
    Savings_Precision_wlosses_m1 = {}

    losses_1 = {}
    losses_0 = {}
    losses_m1 = {}


    for i in range(len(prec_read_0)):

        bought_x_1[i] = prec_read_1.iloc[i].loc['Bought_Grid_Precision'] * 0.15 / 2
        bought_x_0[i] = prec_read_0.iloc[i].loc['Bought_Grid_Precision'] * 0.15 / 2
        bought_x_m1[i] = prec_read_m1.iloc[i].loc['Bought_Grid_Precision'] * 0.15 / 2

        sold_x_1[i] = prec_read_1.iloc[i].loc['Sold_Grid_Precision'] * 0.15 / 2
        sold_x_0[i] = prec_read_0.iloc[i].loc['Sold_Grid_Precision'] * 0.15 / 2
        sold_x_m1[i] = prec_read_m1.iloc[i].loc['Sold_Grid_Precision'] * 0.15 / 2

        losses_1[i] = bought_x_1[i] + sold_x_1[i]
        losses_0[i] = bought_x_0[i] + sold_x_0[i]
        losses_m1[i] = bought_x_m1[i] + sold_x_m1[i]

        Savings_Precision_wlosses_1[i] = prec_read_1.iloc[i].loc['Savings_Precision'] - losses_1[i]
        Savings_Precision_wlosses_0[i] = prec_read_0.iloc[i].loc['Savings_Precision'] - losses_0[i]
        Savings_Precision_wlosses_m1[i] = prec_read_m1.iloc[i].loc['Savings_Precision'] - losses_m1[i]


    prec_read_1['Losses'] = pd.Series(losses_1, index=prec_read_1.index)
    prec_read_0['Losses'] = pd.Series(losses_0, index=prec_read_0.index)
    prec_read_m1['Losses'] = pd.Series(losses_m1, index=prec_read_m1.index)

    prec_read_1['Savings_Precision_withLosses'] = pd.Series(Savings_Precision_wlosses_1, index=prec_read_1.index)
    prec_read_0['Savings_Precision_withLosses'] = pd.Series(Savings_Precision_wlosses_0, index=prec_read_0.index)
    prec_read_m1['Savings_Precision_withLosses'] = pd.Series(Savings_Precision_wlosses_m1, index=prec_read_m1.index)

    batt_i = 0

    batt_read_1, batt_read_0, batt_read_m1 = csv_func_batt(n, batt_i)

    batt_Precision_wlosses_1 = {}
    batt_Precision_wlosses_0 = {}
    batt_Precision_wlosses_m1 = {}

    for i in range(len(batt_read_0)):

        batt_Precision_wlosses_1[i] = batt_read_1.iloc[i].loc['Savings_Precision_WB'] - losses_1[0]
        batt_Precision_wlosses_0[i] = batt_read_0.iloc[i].loc['Savings_Precision_WB'] - losses_0[0]
        batt_Precision_wlosses_m1[i] = batt_read_m1.iloc[i].loc['Savings_Precision_WB'] - losses_m1[0]

    batt_read_1['Batt_Precision_withLosses'] = pd.Series(batt_Precision_wlosses_1, index=batt_read_1.index)
    batt_read_0['Batt_Precision_withLosses'] = pd.Series(batt_Precision_wlosses_0, index=batt_read_0.index)
    batt_read_m1['Batt_Precision_withLosses'] = pd.Series(batt_Precision_wlosses_m1, index=batt_read_m1.index)

    City = 'Porto'

    newpath = f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\Precision\\Losses'
    newpath_batt = f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\Precision\\Losses\\batteries'

    if not os.path.exists(newpath):

        os.makedirs(newpath)


    if not os.path.exists(newpath_batt):

        os.makedirs(newpath_batt)


    prec_read_m1.to_csv(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\Precision\\Losses\\batteries\\{batt_i}panel_{n}euro__panels_m1.csv',
                        index=False, header=True)

    prec_read_1.to_csv(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\Precision\\Losses\\batteries\\{batt_i}panel_{n}euro__panels_m1.csv',
                       index=False, header=True)

    prec_read_0.to_csv(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\Precision\\Losses\\batteries\\{batt_i}panel_{n}euro__panels_m1.csv',
                       index=False, header=True)






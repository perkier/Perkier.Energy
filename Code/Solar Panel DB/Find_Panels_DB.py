import pandas as pd
import pvlib
import re

from Functions_Find_Panels import data_set, interpolating

def module_name(mod):

    part = mod.split('_')

    name = {}

    for i in range(len(part)):

        if part[0] == ' ':

            pass

        else:

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
            name_final = f'{name_final} {name[i]}'

    return name_final


def searched_deco(panel):

    mod = module_name(panel).split(' ')

    array = re.findall(r'[0-9]+', module_name(panel))

    try:

        for i in range(len(array)):

            tw = int(array[i])
            if 999 > tw > 10:
                Power = array[i]

            i = i+1

    except:

        pass

    brand = mod[1]
    year = mod[len(mod) - 1]

    try:

        panel_nameinfo = {'Brand': brand, 'Year': year, 'Power': Power}

    except:

        panel_nameinfo = {'Brand': brand, 'Year': year, 'Power': 'No info'}

    panel_nameinfo = pd.Series(panel_nameinfo)

    factor = {}

    for i in range(2, len(mod)):

        factor[i - 2] = mod[i]

    factor = pd.Series(factor)
    panel_nameinfo = panel_nameinfo.append(factor)

    return panel_nameinfo


sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

modules = sandia_modules.T.reset_index().loc[: , 'index']

name_array = {}
unchanged_name_array = {}
brand_array = {}

j = 0

for i in range(len(modules)):

    try:

        name_array[i] = module_name(modules.iloc[i])
        unchanged_name_array[i] = modules.iloc[i]

    except:

        j += 1

    try:

        brand_array[i] = searched_deco(modules.iloc[i]).loc['Brand']

    except:

        j += 1


modules = pd.DataFrame({'Brand': brand_array,
                        'Module_Name': name_array,
                        'Unchanged_Name': unchanged_name_array}).sort_values(by='Brand').reset_index(drop=True)


modules = modules.loc[:,'Brand'].drop_duplicates().reset_index(drop=True)


prices_reader_1 = open('C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\CODE\\Google API\\prices.csv', 'rb')
prices_read_1 = pd.read_csv(prices_reader_1, encoding='latin1').loc[:, 'Brand']
prices_reader_1.close()

prices_reader_2 = open('C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\CODE\\Google API\\prices_solar_2.csv', 'rb')
prices_read_2 = pd.read_csv(prices_reader_2, encoding='latin1').loc[:, 'Brand']
prices_reader_2.close()

df_row_reindex = pd.concat([prices_read_1, prices_read_2], ignore_index=True).drop_duplicates().sort_values().reset_index(drop=True)

array_row_reindex = {}

for i in range(len(df_row_reindex)):

    array_row_reindex[i] = searched_deco(df_row_reindex.iloc[i]).values[0].split(' ')[0]

df_row_reindex = pd.DataFrame({'Brand': array_row_reindex})

iguais = {}
k = 0

for i in range(len(df_row_reindex)):

    for j in range(len(modules)):

        if modules[j] == array_row_reindex[i]:

            iguais[k] = array_row_reindex[i]
            k += 1

panels_iguais = {}
index_num = {}
k =0

name_df = pd.DataFrame({'Panel_Name': name_array})

unchanged_name_iguais = {}

for i in range(len(name_df)):

    for j in range(len(iguais)):

        if name_df.iloc[i].loc['Panel_Name'].split(' ')[1] == iguais[j]:

            panels_iguais[k] = name_df.iloc[i].loc['Panel_Name']
            index_num[k] = i
            unchanged_name_iguais[k] = unchanged_name_array[i]
            k += 1

Watts_Panels_Array = {}
Brand_Panels_Array = {}

for i in range(len(panels_iguais)):

    Watts_Panels_Array[i] = searched_deco(panels_iguais[i]).loc['Power']
    Brand_Panels_Array[i] = panels_iguais[i].split(' ')[1]


panels_iguais_df = pd.DataFrame({'Panel_Name': panels_iguais,
                                 'Brand_Name': Brand_Panels_Array,
                                 'Sandia_Index': index_num,
                                 'Sandia_Name': unchanged_name_iguais,
                                 'Power': Watts_Panels_Array}).sort_values(by='Panel_Name').reset_index(drop=True)

panels_iguais_df = panels_iguais_df.loc[panels_iguais_df.loc[:, 'Power'] != 'No info'].reset_index(drop=True)








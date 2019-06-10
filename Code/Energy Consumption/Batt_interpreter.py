import pandas as pd
import numpy as np
import pvlib
import time
import os

from sazonal_consumption import final_df
from CONSUMPTION_FUNC import df_original


def cons_func(money):

    profile = {'Type': 'One Student',
               'Month Bill': 5,
               'Bill': money}

    Price_kWh = 0.2284

    kWh_month = profile['Bill'] / Price_kWh

    # print(kWh_month)

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

    return consum_Wh


def modules(sandia_names, module_price, module_num, bill_money):

    native_times = pd.date_range(start='1999-01-01', end='2019-01-01', freq='1h')

    timezone = 'Etc/GMT-5'
    latitude = 41.1496100
    longitude = -8.6109900
    City = 'Porto'
    altitude = 7

    newpath = f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\Precision'

    if not os.path.exists(newpath):

        os.makedirs(newpath)


    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    module = sandia_modules[sandia_names]

    sapm_inverters = pvlib.pvsystem.retrieve_sam('CECinverter')
    inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']

    temp_air = 20
    wind_speed = 0

    system = {'module': module, 'inverter': inverter, 'surface_azimuth': 180}

    system['surface_tilt'] = latitude
    system['surface_azimuth'] = 180


    times = native_times.tz_localize(timezone)

    solpos = pvlib.solarposition.get_solarposition(times, latitude, longitude)

    dni_extra = pvlib.irradiance.get_extra_radiation(times)

    airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
    pressure = pvlib.atmosphere.alt2pres(altitude)
    am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)

    # tl = pvlib.clearsky.lookup_linke_turbidity(times, latitude, longitude)
    tl = 2

    cs = pvlib.clearsky.ineichen(solpos['apparent_zenith'], am_abs, tl,
                                 dni_extra=dni_extra, altitude=altitude)

    aoi = pvlib.irradiance.aoi(system['surface_tilt'], system['surface_azimuth'],
                               solpos['apparent_zenith'], solpos['azimuth'])

    total_irrad = pvlib.irradiance.get_total_irradiance(system['surface_tilt'], system['surface_azimuth'],
                                                        solpos['apparent_zenith'], solpos['azimuth'], cs['dni'],
                                                        cs['ghi'], cs['dhi'],
                                                        dni_extra=dni_extra, model='haydavies')

    temps = pvlib.pvsystem.sapm_celltemp(total_irrad['poa_global'], wind_speed, temp_air)

    i = 0
    module_names = {}
    effective_irradiance = {}
    dc = {}
    ac = {}
    annual_energy = {}
    energies = {}
    savings_array = {}
    savings_array_more = {}
    n = {}
    Price_euro_kWh = 0.2284

    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(total_irrad['poa_direct'],
                                                                    total_irrad['poa_diffuse'],
                                                                    am_abs,
                                                                    aoi,
                                                                    module)

    dc = pvlib.pvsystem.sapm(effective_irradiance, temps['temp_cell'], module)
    ac = pvlib.pvsystem.snlinverter(dc['v_mp'], dc['p_mp'], inverter)

    ac = ac * module_num

    annual_energy = ac.sum() / 20
    energies = annual_energy

    energies = pd.Series(energies)
    energ_pd = pd.DataFrame({'Yearly Prod. (W hr)': energies})

    # df = pd.merge(coord_pd, energ_pd, left_index=True, right_index=True, how='outer')
    # df = df.sort_values(by='Yearly Prod. (W hr)', ascending=False)
    # print(df)
    # print('\n')

    ac_df = pd.DataFrame([ac]).T
    ac_df = ac_df[0].reset_index()
    ac_df.columns = ['Hour', 'Watt-hour']

    consumo = consumption(bill_money)

    Battery_Capacity_kWh = 0
    Battery_Capacity_Wh = Battery_Capacity_kWh * 1000
    Battery_Price = 0

    k = 0

    Grid_Power = {}
    Grid_Buying_Power = {}
    Grid_Selling_Power = {}

    batt_aux = 0

    for k in range(len(ac_df)):

        Grid_Power[k] = consumo[k] - ac_df.iloc[k].loc['Watt-hour']

            if Grid_Power[k] < 0:

                Grid_Buying_Power[k] = 0
                Grid_Selling_Power[k] = Grid_Power[k]

            if Grid_Power[k] > 0:

                Grid_Buying_Power[k] = Grid_Power[k]
                Grid_Selling_Power[k] = 0

    ac_df['Buy Wh to the grid'] = pd.Series(Grid_Buying_Power, index=ac_df.index)
    ac_df['Sell Wh to the grid'] = pd.Series(Grid_Selling_Power, index=ac_df.index)

    Buying_euro_kWh = 0.2284
    Selling_euro_kWh = 0.05

    Total_bought_grid = ac_df.loc[:, "Buy Wh to the grid"].sum()
    Bought_euro_grid = Total_bought_grid / 1000 * Buying_euro_kWh

    Total_sold_grid = ac_df.loc[:, "Sell Wh to the grid"].sum()
    Sold_euro_grid = abs(Total_sold_grid / 1000 * Selling_euro_kWh)

    # Total_Price = Battery_Price + Bought_euro_grid - Sold_euro_grid + (module_price * module_num)

    Total_without_Batt = consumo.sum()
    euro_without_Batt = Total_without_Batt * Buying_euro_kWh / 1000

    savings = euro_without_Batt - Bought_euro_grid - (module_price * module_num) + Sold_euro_grid

    savings_array_more = (ac_df.loc[:, 'Watt-hour'].sum() * Buying_euro_kWh / 1000) - (module_price * module_num)

    pricing = module_price * module_num

    equivalente = ac_df.loc[:, 'Watt-hour'].sum() * Buying_euro_kWh / 1000

    return savings, Sold_euro_grid, Bought_euro_grid, euro_without_Batt


def csv_func(num):

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

    return csv_read_1, csv_read_0, csv_read_m1


def main():

    start_time = time.time()

    x = 1

    for n in range(50, 105, 5):

        loop_time = time.time()
        csv_read_1, csv_read_0, csv_read_m1 = csv_func(n)

        real_savings_array_m1 = {}
        real_savings_array_1 = {}
        real_savings_array_0 = {}

        real_sold_array_m1 = {}
        real_sold_array_1 = {}
        real_sold_array_0 = {}

        real_bought_array_m1 = {}
        real_bought_array_1 = {}
        real_bought_array_0 = {}

        euro_without_array_m1 = {}
        euro_without_array_1 = {}
        euro_without_array_0 = {}

        k = 1

        for i in range(5):

            real_savings_array_m1[i], real_sold_array_m1[i], real_bought_array_m1[i], euro_without_array_m1[i] = modules(csv_read_m1.iloc[i].loc['Sandia_Name'], csv_read_m1.iloc[i].loc['Module_Price'], csv_read_m1.iloc[i].loc['Recomended_Panels'], n)

            print(f'{n}: {k}/15 DONE -', "%.2f" %(x * 100 / 165), '%')

            k += 1
            x += 1

            real_savings_array_1[i], real_sold_array_1[i], real_bought_array_1[i], euro_without_array_1[i] = modules(csv_read_1.iloc[i].loc['Sandia_Name'], csv_read_1.iloc[i].loc['Module_Price'], csv_read_1.iloc[i].loc['Recomended_Panels'], n)

            print(f'{n}: {k}/15 DONE -', "%.2f" %(x * 100 / 165), '%')
            # print(f'{n}: {k}/15 DONE - {x * 100 / 165}%')

            k += 1
            x += 1

            real_savings_array_0[i], real_sold_array_0[i], real_bought_array_0[i], euro_without_array_0[i] = modules(csv_read_0.iloc[i].loc['Sandia_Name'], csv_read_0.iloc[i].loc['Module_Price'], csv_read_0.iloc[i].loc['Recomended_Panels'], n)

            print(f'{n}: {k}/15 DONE -', "%.2f" %(x * 100 / 165), '%')

            k += 1
            x += 1

        print(f"--- {time.time() - loop_time} seconds for {n}---")

        City = 'Porto'

        csv_read_m1['Savings_Precision'] = pd.Series(real_savings_array_m1, index=csv_read_m1.index)
        csv_read_m1['Sold_Grid_Precision'] = pd.Series(real_sold_array_m1, index=csv_read_m1.index)
        csv_read_m1['Bought_Grid_Precision'] = pd.Series(real_bought_array_m1, index=csv_read_m1.index)
        csv_read_m1['Euros_Without_Panels'] = pd.Series(euro_without_array_m1, index=csv_read_m1.index)

        csv_read_1['Savings_Precision'] = pd.Series(real_savings_array_1, index=csv_read_1.index)
        csv_read_1['Sold_Grid_Precision'] = pd.Series(real_sold_array_1, index=csv_read_1.index)
        csv_read_1['Bought_Grid_Precision'] = pd.Series(real_bought_array_1, index=csv_read_1.index)
        csv_read_1['Euros_Without_Panels'] = pd.Series(euro_without_array_1, index=csv_read_1.index)

        csv_read_0['Savings_Precision'] = pd.Series(real_savings_array_0, index=csv_read_0.index)
        csv_read_0['Sold_Grid_Precision'] = pd.Series(real_sold_array_0, index=csv_read_0.index)
        csv_read_0['Bought_Grid_Precision'] = pd.Series(real_bought_array_0, index=csv_read_0.index)
        csv_read_0['Euros_Without_Panels'] = pd.Series(euro_without_array_0, index=csv_read_0.index)

        csv_read_m1.to_csv(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\Precision\\{n}euro__panels_m1.csv', index=False, header=True)
        csv_read_1.to_csv(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\Precision\\{n}euro__panels_1.csv', index=False, header=True)
        csv_read_0.to_csv(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\Precision\\{n}euro__panels_0.csv', index=False, header=True)

    print('-'*50)
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":

    main()

"""

--- 5803.467513084412 seconds ---

"""
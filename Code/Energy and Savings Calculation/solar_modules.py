import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pvlib
import time
import os
import pylab
import csv

from prices_aux import panels_iguais_df
from AC_helper import yearly_consum_Wh
from CONSUMPTION_FUNC import profile

def sm(num):

    start_time = time.time()

    native_times = pd.date_range(start='1999-01-01', end='2019-01-01', freq='1h')

    timezone = 'Etc/GMT-5'
    latitude = 41.1496100
    longitude = -8.6109900
    City = 'Porto'

    newpath = f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}'

    if not os.path.exists(newpath):

        os.makedirs(newpath)

    altitude = 7

    module = {}
    system = {}

    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

    module = {}
    i = 0

    for i in range(len(panels_iguais_df)):

        module[i] = sandia_modules[panels_iguais_df.iloc[i].loc['Sandia_Name']]

    sapm_inverters = pvlib.pvsystem.retrieve_sam('CECinverter')
    inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']

    temp_air = 20
    wind_speed = 0

    i = 0

    for i in range(len(module)):

        system[i] = {'module': module[i], 'inverter': inverter}

    system['surface_tilt'] = latitude
    system['surface_azimuth'] = 180

    energies = {}

    i = 0
    # print('\n')
    # print(system)

    times = native_times.tz_localize(timezone)

    # for i in range(len(system)):
    #     system['surface_tilt'] = latitude

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

    for i in range(len(module)):

        effective_irradiance[i] = pvlib.pvsystem.sapm_effective_irradiance(total_irrad['poa_direct'],
                                                                           total_irrad['poa_diffuse'], am_abs, aoi, module[i])

        dc[i] = pvlib.pvsystem.sapm(effective_irradiance[i], temps['temp_cell'], module[i])
        ac[i] = pvlib.pvsystem.snlinverter(dc[i]['v_mp'], dc[i]['p_mp'], inverter)

        ac_df = pd.DataFrame([ac]).T
        ac_df = ac_df[0].reset_index()
        ac_df.columns = ['Hour', 'Watt-hour']

        annual_energy[i] = ac[i].sum() / 20

        n[i] = int(yearly_consum_Wh / annual_energy[i]) + num

        # annual_energy_more[i] = ac[i].sum() * int(n)

        energies[i] = annual_energy[i]

        savings_array[i] = ac[i].sum() * Price_euro_kWh / 1000 - panels_iguais_df.iloc[i].loc['Price']

        savings_array_more[i] = ( ac[i].sum() * n[i] * Price_euro_kWh / 1000 ) - ( panels_iguais_df.iloc[i].loc['Price'] * n[i] )

        # try:
        #
        #     savings_array[i] = (consum_Wh - ac_df.loc[:, 'Watt-hour']) * Price_euro_kWh / 1000
        #     savings_array[i] = savings_array[i].sum()
        #
        # except:
        #
        #     savings_array[i] = 'To_Be_Deleted'


        i = i + 1

    print('\n')

    energ = pd.Series(energies)
    # print(energ)

    names = pd.Series(module_names)
    # print(names)

    # print('\n')

    energ_pd = {}
    energ_pd = pd.DataFrame({'Module': panels_iguais_df.loc[:, 'Panel_Name'],
                             'Sandia_Name': panels_iguais_df.loc[:, 'Sandia_Name'],
                             'Module_Price': panels_iguais_df.loc[:, 'Price'],
                             'Power': panels_iguais_df.loc[:, 'Power'],
                             'Yearly Prod. (W hr)': energ,
                             'Savings': savings_array,
                             'Recomended_Panels': n,
                             'Recom_Panels_Savings': savings_array_more})

    energ_pd = energ_pd.sort_values(by= 'Recom_Panels_Savings', ascending= False).reset_index(drop=True)

    print(energ_pd)

    # energ_pd.set_index('Module', inplace=True)

    #  df = pd.concat([coord_pd, energ_pd])
    #  print(df)
    print('\n'*2)

    print("--- %s seconds ---" % (time.time() - start_time))

    # df = pd.merge(coord_pd, energ_pd, left_index=True, right_index=True, how='outer')
    # print(df)
    print('\n')

    print(energ_pd.iloc[2])

    # energies.plot(kind='bar', rot=0)
    # plt.ylabel('Yearly energy yield (W hr)')
    # pylab.show()

    print('\n')

    profile_bill = profile['Bill']

    energ_pd.to_csv(f'C:\\Users\\Diogo Sá\\Desktop\\perkier tech\\Energy\\Final_Calcs\\{City}\\{profile_bill}euro__panels_{num}.csv', index=False, header=True)


sm(-1)
sm(0)
sm(1)

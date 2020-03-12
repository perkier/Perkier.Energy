import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pvlib
import time
import numpy as np
import pylab
import copy

class equipment(object):

    def __init__(self):

        pass

    def battery_data(self):

        prices_reader = open('C:\\Users\\diogo\\Desktop\\perkier tech\\Energy\\CODE\\Google API\\Prices_batteries.csv', 'rb')
        prices_read = pd.read_csv(prices_reader, encoding='latin1')
        prices_reader.close()

        Battery_Prices = prices_read.loc[:,'Price [$]']
        Battery_Storage = prices_read.loc[:,'Energy Storage [kWh]']
        Battery_Warranty = prices_read.loc[:,'Warranty Years']

        Effective_Cost = Battery_Storage.mul(Battery_Warranty)
        Effective_Cost = Battery_Prices.div(Effective_Cost)

        prices_read['Effective Cost'] = pd.Series(Effective_Cost, index=prices_read.index)
        prices_read = prices_read.sort_values(by=['Effective Cost']).reset_index(drop=True)

        return prices_read


class location(object):

    def __init__(self):

        self.time_range()
        self.coordinates()

    def time_range(self):

        self.native_times = pd.date_range(start='2012-01-01', end='2014-02-28', freq='30min')

        return self.native_times


    def coordinates(self):

        # latitude, longitude, name, altitude, timezone
        timezone = 'Etc/GMT-5'
        latitude = 41.1496100
        longitude = -8.6109900
        altitude = 35
        City = 'Porto'

        self.coords = {'tzone': timezone,
                       'lat': latitude,
                       'long': longitude,
                       'alt': altitude,
                       'city': City}

        return self.coords


    def solar_radiation(self):

        times = self.native_times.tz_localize(self.coords['tzone'])

        self.solpos = pvlib.solarposition.get_solarposition(times,
                                                            self.coords['lat'],
                                                            self.coords['long'])

        # dni_extra = pvlib.irradiance.get_extra_radiation(times, method='nrel')
        self.dni_extra = pvlib.irradiance.extraradiation(times, method='nrel')

        # airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
        airmass = pvlib.atmosphere.relativeairmass(self.solpos['apparent_zenith'])
        pressure = pvlib.atmosphere.alt2pres(self.coords['alt'])
        # self.am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
        self.am_abs = pvlib.atmosphere.absoluteairmass(airmass, pressure)

        tl = pvlib.clearsky.lookup_linke_turbidity(times, self.coords['lat'], self.coords['long'])
        # tl = 2
        self.cs = pvlib.clearsky.ineichen(self.solpos['apparent_zenith'], self.am_abs, tl,
                                          dni_extra=self.dni_extra,
                                          altitude=self.coords['alt'])

        return self.solpos, self.cs, self.dni_extra, self.am_abs
        

class consumer(object):

    def __init__(self, code, consumer_info_df, location):

        self.location = location

        self.solar_panel_name = consumer_info_df.loc['Solar_Panel_Module']
        self.solar_panel_num = consumer_info_df.loc['Num_Solar_Panels']
        self.battery_name = consumer_info_df.loc['Battery_Model']

        self.electrical_consumption(code)

        if self.solar_panel_name != 'None':

            self.solar_panels()
            self.solar_production()
            
        else:

            self.ac = pd.Series(np.full(shape=len(self.location.native_times), fill_value=0), index=self.location.native_times)

        if self.battery_name != 'None':

            eq = equipment()
            batt_prices = eq.battery_data()
            self.batt_info = batt_prices.loc[batt_prices['Model'] == self.battery_name].reset_index(drop=True).iloc[0]

            self.battery()

    
    def solar_panels(self, inverter_name = 'ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_'):

        sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

        self.module = sandia_modules[self.solar_panel_name]

        sapm_inverters = pvlib.pvsystem.retrieve_sam('CECinverter')
        self.inverter = sapm_inverters[inverter_name]

        self.system = {'module': self.module, 'inverter': self.inverter, 'surface_azimuth': 180}
    
    
    def battery(self):

        self.brand = self.batt_info.loc['Brand']
        self.model = self.batt_info.loc['Model']
        self.batt_capacity = self.batt_info.loc['Energy Storage [kWh]']
        self.batt_price = self.batt_info.loc['Price [$]']
        

    def electrical_consumption(self, code):
        
        path = "C:\\Users\\diogo\\Desktop\\perkier tech\\Energy\\DATA\\Smart meters in London\\halfhourly_dataset\\block_47.csv"

        cons_reader = open(path,'rb')
        cons_read = pd.read_csv(cons_reader, encoding='latin1')
        cons_reader.close()

        self.consum_df = cons_read.loc[cons_read['LCLid'] == code].reset_index(drop=True)


    def solar_production(self):

        solpos, cs, dni_extra, am_abs = self.location.solar_radiation()

        temp_air = 20
        wind_speed = 0

        self.coords = self.location.coords
        self.system['surface_tilt'] = self.coords['lat']
        self.system['surface_azimuth'] = 180

        self.total_irrad = pvlib.irradiance.total_irrad(self.system['surface_tilt'],
                                                        self.system['surface_azimuth'],
                                                        solpos['apparent_zenith'],
                                                        solpos['azimuth'],
                                                        cs['dni'], cs['ghi'], cs['dhi'],
                                                        dni_extra=dni_extra,
                                                        model='haydavies')

        self.temps = pvlib.pvsystem.sapm_celltemp(self.total_irrad['poa_global'],
                                                  wind_speed,
                                                  temp_air)

        self.aoi = pvlib.irradiance.aoi(self.system['surface_tilt'], self.system['surface_azimuth'],
                                        solpos['apparent_zenith'], solpos['azimuth'])

        effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(self.total_irrad['poa_direct'],
                                                                        self.total_irrad['poa_diffuse'],
                                                                        am_abs,
                                                                        self.aoi,
                                                                        self.module)

        dc = pvlib.pvsystem.sapm(effective_irradiance, self.temps['temp_cell'], self.module)
        self.ac = pvlib.pvsystem.snlinverter(dc['v_mp'], dc['p_mp'], self.inverter)

        # self.annual_energy = self.ac.sum() / 20
        # energies[name] = annual_energy


def main():
    
    pass
    
if __name__ == '__main__':
    
    main()

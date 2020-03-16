import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pvlib
import time
import numpy as np
import pylab
import copy

buying = 0.02
selling = 0.015

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

        self.native_times = pd.date_range(start='2011-11-22', end='2014-02-28', freq='30min')

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


class electricity_prices(object):
    
    def __init__(self):
        
        self.buying = 0.02
        self.selling = 0.015
        

class consumer(object):

    def __init__(self, code, consumer_info_df, location):

        self.location = location

        self.start_wallet()

        self.batt_level = 0

        self.solar_panel_name = consumer_info_df.loc['Solar_Panel_Module']
        self.solar_panel_num = consumer_info_df.loc['Num_Solar_Panels']
        self.battery_name = consumer_info_df.loc['Battery_Model']
        self.cons_code = code

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

        else:

            self.batt_capacity = 0


    def start_wallet(self):

        self.wallet = pd.DataFrame({'Date': [],
                                    'Bought[kW]': [],
                                    'Bought[€]': [],
                                    'Sold[kW]': [],
                                    'Sold[€]': [],
                                    'Balance[kW]': [],
                                    'Balance[€]': []})


    def transaction_wallet(self, sold, bought, date):
        
        balance_kWh = sold - bought
        balance_money = (sold * selling/ 1000) - (bought * buying / 1000)

        to_append = pd.DataFrame({'Date': [date],
                                  'Bought[kW]': [bought / 1000],
                                  'Bought[€]': [bought * buying / 1000],
                                  'Sold[kW]': [sold / 1000],
                                  'Sold[€]': [sold * selling/ 1000],
                                  'Balance[kW]': [balance_kWh],
                                  'Balance[€]': [balance_money]})

        self.wallet = pd.concat([self.wallet, to_append], ignore_index=True)

    
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
        self.ac = pvlib.pvsystem.snlinverter(dc['v_mp'], dc['p_mp'], self.inverter).fillna(0).clip(lower=0)
        self.ac = self.ac * self.solar_panel_num

        # self.annual_energy = self.ac.sum() / 20
        # energies[name] = annual_energy


    # def energy_bank(self):
    # 
    #     print(self.ac.head())
    #     print(self.consum_df.head())
    #     print(self.batt_capacity)




class energy_bank(object):

    def __init__(self, consumers):

        self.consumers = consumers

        self.time_loop()


    def sell_energy(self, balance, consumer):

        sold = balance
        bought = 0

        # print(time, produced, consumed, consumer.cons_code, balance, consumer.batt_level,
        #       'Sell Energy to the Grid')

        return sold, bought

    def buy_energy(self, balance, consumer):

        sold = 0
        bought = abs(balance)

        # print(time, produced, consumed, consumer.cons_code, balance, consumer.batt_level,
        #       'Buy Energy from the Grid')

        return sold, bought


    def store_energy(self, balance, consumer):

        consumer.batt_level += balance

        sold = 0
        bought = 0

        if consumer.batt_level > consumer.batt_capacity:

            extra = consumer.batt_level - consumer.batt_capacity
            consumer.batt_level = consumer.batt_capacity

            sold, bought = self.sell_energy(self, extra, consumer)

        # print(time, produced, consumed, consumer.cons_code, balance, consumer.batt_level,
        #       'Give energy to the battery')

        return sold, bought


    def use_batt(self, balance, consumer):

        consumer.batt_level += balance

        sold = 0
        bought = 0

        if consumer.batt_level < 0:

            extra = abs(consumer.batt_level)
            consumer.batt_level = 0

            sold, bought = self.buy_energy(extra, consumer)

        # print(time, produced, consumed, consumer.cons_code, balance, consumer.batt_level,
        #       'Take energy From battery')

        return sold, bought


    def banking(self, produced, consumed, consumer, date):

        balance = produced - consumed

        # print(consumer.batt_level)

        if balance >= 0:

            if consumer.batt_capacity <= (consumer.batt_level + balance):

                sold, bought = self.sell_energy(balance, consumer)

            else:

                sold, bought = self.store_energy(balance, consumer)


        if balance < 0:

            if consumer.batt_level > 0:

                sold, bought = self.use_batt(balance, consumer)

            else:

                sold, bought = self.buy_energy(balance, consumer)

        # print(batt_level)
        # print(batt_capacity)

        consumer.transaction_wallet(sold, bought, date)

        # quit()


    def time_loop(self):

        time_line = self.consumers[0].consum_df.loc[:,'tstp']

        for time in time_line:

            for consumer in self.consumers:

                ac_df = consumer.ac
                consum_df = consumer.consum_df

                try:
                    produced = ac_df[time]

                except:
                    produced = 0

                try:
                    consumed = float(consum_df.loc[consum_df['tstp'] == time].reset_index(drop=True).iloc[0].loc['energy(kWh/hh)']) * 1000

                except:
                    consumed = 0

                self.banking(produced, consumed, consumer, time)



        # quit()
        # 
        # print(time_line)
        # quit()



def main():
    
    pass
    
if __name__ == '__main__':
    
    main()

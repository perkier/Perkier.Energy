from CoolProp.CoolProp import PropsSI, PhaseSI, HAPropsSI

def room_conditions():

    A_sala = 10*2.5*2 + 5*2.5*2 + 10*5
    h_sala = 0.6
    V_sala = 10*5*2.5

    P_int = 101325

    return A_sala, h_sala, V_sala, P_int


def sub_heating(fluid):

    T_cond = 35
    P_cond = PropsSI('P','T',T_cond + 273.15,'Q',0,fluid)

    T_evap = -10
    P_evap = PropsSI('P','T',T_evap + 273.15,'Q',1,fluid)

    Delta_T_sh = 5
    eta_comp = 0.9

    return T_cond, P_cond, T_evap, P_evap, Delta_T_sh, eta_comp


def Nominal_values(fluid, P_evap, P_cond, T_evap, DELTAT_sh, eta_comp):

    A_sala, h_sala, V_sala, P_int = room_conditions()

    P_simp = {}
    T_simp = {}
    h_simp = {}
    s_simp = {}

    # Estado 1
    P_simp[0] = P_evap
    T_simp[0] = T_evap + DELTAT_sh
    h_simp[0] = PropsSI('H','P', P_simp[0],'T', T_simp[0]+273.15,fluid)
    s_simp[0] = PropsSI('S','P', P_simp[0],'T', T_simp[0]+273.15,fluid)

    # Estado 2
    P_simp[1] = P_cond
    s_simp[1] = s_simp[0]
    h_2i_simp = PropsSI('H','P', P_simp[1],'S', s_simp[1],fluid)
    h_simp[1] = h_simp[0] + eta_comp*(h_2i_simp - h_simp[0])

    # Calculo da potencia maxima [W] que a bomba de calor deve ter
    Pot_Nominal = h_sala * A_sala * ( 24 - 0.1 )

    # Calculo do caudal mássico [kg/s] do fluido na bomba de calor
    m_dot_fl =  Pot_Nominal / (h_simp[1] - h_simp[0])

    return Pot_Nominal, m_dot_fl


def heat_states(P_evap, T_evap, P_cond, T_cond, DeltaT_sh, fluid, eta_comp, m_dot_fluid):

    # State 1
    P_1 = P_evap
    T_1 = T_evap + DeltaT_sh
    h_1 = PropsSI('H', 'P', P_1, 'T', T_1+273.15, fluid)
    s_1 = PropsSI('S', 'P', P_1, 'T', T_1+273.15, fluid)

    # State 2
    P_2 = P_cond
    s_2i = s_1
    h_2i = PropsSI('H', 'P', P_2, 'S', s_2i, fluid)
    h_2 = h_1 + eta_comp * (h_2i - h_1)
    s_2 = PropsSI('S', 'P', P_2, 'H', h_2, fluid)
    T_2 = PropsSI('T', 'P', P_2, 'S', s_2, fluid)

    # State 3
    P_3 = P_cond
    T_3 = T_cond
    h_3 = PropsSI('H', 'T', T_3+273.15, 'Q', 0, fluid)
    s_3 = PropsSI('S', 'T', T_3+273.15, 'Q', 0, fluid)

    # State 4
    P_4 = P_evap
    h_4 = h_3
    s_4 = PropsSI('S', 'P', P_4, 'H', h_4, fluid)
    T_4 = PropsSI('T', 'P', P_4, 'S', s_4, fluid)

    Q_dot_evap = m_dot_fluid * (h_1 - h_4)
    Q_dot_cond = m_dot_fluid * (h_2 - h_3)
    Q_dot_exp = m_dot_fluid * (h_4 - h_3)
    Q_dot_comp = m_dot_fluid * (h_2 - h_1)

    return Q_dot_evap, Q_dot_cond, Q_dot_exp, Q_dot_comp


def evaporator(m_dot_fluid, T_amb, fluid):

    # Comprimento do evaporador - m
    W = 0.2

    # Altura do evaporador - m
    Alt_evap = 0.2

    # Area Frontal do evaporador - m^2
    A_frontal = W * Alt_evap

    # T_evap é 10ºC a baixo da temperatura minima do ar
    T_evap = min(T_amb) - 10

    P_evap = PropsSI('P','T', T_evap + 273.15,'Q',1,fluid)

    v_air = 3
    m_dot_air = v_air * A_frontal * 0.8

    return P_evap, T_evap


def amb_temp():

    T_amb = [5.1, 4.8, 3.5, 10]

    return T_amb



def heat_room(Q_dot, T_amb, i):

    A_sala, h_sala, V_sala, P_int = room_conditions()

    # Caudal Volumico de ar renovado
    V_dot_renov = 0.7 * (10 ^ (-3)) / 3600

    # CP do ar renovado
    cp_renov = PropsSI('CPMASS','T', T_amb[i] + 273.15,'P',P_int, 'Air')

    # Caudal Massico de ar Renovado
    m_dot_renov = V_dot_renov * PropsSI('D','T', T_amb[i] + 273.15,'P',P_int, 'Air')

    # Caudal Massico da Sala
    m_dot_int = V_sala * PropsSI('D','T', T_amb[i] + 273.15,'P',P_int, 'Air')

    print(Q_dot)
    print(T_amb[i]) 

    # Transferencia de calor entre inicio da sala e final da sala
    # heat_ex_1 = m_dot_int * PropsSI('CPMASS','T', (T_int[i]+T_int[i-1])/2 + 273.15,'P',P_int, 'Air') * (T_int[i] - T_int[i-1])

    # Transferencia de calor entre a sala e o exterior
    # heat_ex_2 = A_sala * h_sala * (T_int[i] - T_amb[i])

    # Transferencia de calor entre o ar renovado e o ar da sala
    # heat_ex_1 = m_dot_renov * PropsSI('CPMASS', 'T', (T_amb[i] + T_int[i]) / 2 + 273.15, 'P', P_int, 'Air') * (T_int[i] - T_amb[i])


def main():

    fluid = 'R125'

    i = 3

    T_cond, P_cond, T_evap, P_evap, Delta_T_sh, eta_comp = sub_heating(fluid)

    Pot_Nominal, m_dot_fluid = Nominal_values(fluid, P_evap, P_cond, T_evap, Delta_T_sh, eta_comp)

    T_amb = amb_temp()

    P_evap, T_evap = evaporator(m_dot_fluid, T_amb, fluid)

    Q_dot_evap, Q_dot_cond, Q_dot_exp, Q_dot_comp = heat_states(P_evap, T_evap, P_cond, T_cond, Delta_T_sh, fluid, eta_comp, m_dot_fluid)

    heat_room(Q_dot_cond, T_amb, i)


if __name__ == '__main__':

    main()
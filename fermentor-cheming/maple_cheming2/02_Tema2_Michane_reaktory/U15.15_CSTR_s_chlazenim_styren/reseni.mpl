# ==============================================================================
# U15.15 Prutocny michany reaktor s chladicim hadem - vyroba styrenu
# ChI II - Tema 2: Michane reaktory
# Ocekavany vysledek: a) T = 370 K (370.15 K), b) T_chlad = 363 K (362.9 K)
# ==============================================================================
restart;

# Zadani
m_dot_rok := 500e3:      # kg/rok smesi
h_rok     := 8000:       # h/rok
x_S0      := 0.92:       # molarni zlomek styrenu na vstupu
x_B0      := 0.08:       # molarni zlomek butadienu
zeta      := 0.30:       # pozadovana konverze styrenu
V_R       := 1.8:        # m3, objem reaktoru
S_T       := 7.5:        # m2, teplosmenna plocha hadu
T_vstup   := 308:        # K
A_pre     := 3.3e11:     # m^1.5 kmol^-0.5 h^-1, predexponencialni faktor
E_a       := 96790:      # J/mol, aktivacni energie
R_g       := 8.314:      # J/(mol K)
dh_r      := -69140:     # kJ/kmol (= -69.14 kJ/mol)
cp_smes   := 1.886:      # kJ/(kg K)
K_T       := 84:         # kJ/(m2 h K), soucinitel prostupu tepla
rho       := 870:        # kg/m3
M_S := 104.152:  M_B := 54.092:    # kg/kmol

# 1. Molarni hmotnost smesi a vstupni koncentrace styrenu
M_smes := x_S0*M_S + x_B0*M_B;             # kg/kmol
c_S0   := rho*x_S0/M_smes;                 # kmol/m3
c_S    := c_S0*(1 - zeta);                 # kmol/m3, v reaktoru (= vystup)

# 2. Latkova bilance CSTR: V_dot*(c_S0 - c_S) = r*V_R
m_dot := m_dot_rok/h_rok;                  # kg/h
V_dot := m_dot/rho;                        # m3/h
r     := V_dot*(c_S0 - c_S)/V_R;           # kmol/(m3 h)

# 3. a) Rychlostni konstanta a teplota reaktoru z Arrheniovy rovnice
k := r/c_S^1.5;
T := -E_a/(R_g*ln(k/A_pre));               # K

# 4. b) Entalpicka bilance (ref. teplota T):
#    0 = m_dot*cp*(T_vstup - T) + r*V_R*(-dh_r) + K_T*S_T*(T_chlad - T)
T_chlad := fsolve(0 = m_dot*cp_smes*(T_vstup - T) + r*V_R*(-dh_r) + K_T*S_T*(T_c - T), T_c);

printf("a) T = %.2f K,  b) T_chlad = %.2f K\n", T, T_chlad);

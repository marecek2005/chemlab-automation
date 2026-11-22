# ==============================================================================
# U7.12 Spalovani uhli v kotli - generator pary (reseni pres rozsah reakce)
# ChI II - Tema 1: Bilance
# Ocekavany vysledek: a) Q = 20 911 kJ (na 8 kg pary), m_para' = 7.62 kg
#   b) xi = 83.33 mol, dh_r(500 degC) = -390.5 kJ/mol, Q = 23.80 MJ, m_para = 9.10 kg
# Pozn.: druhe oficialni reseni (fiktivni proudy) dava stejne vysledky
#   (a) 7.61 kg, b) 9.10 kg).
# ==============================================================================
restart;

# ---------------- a) generator pary ----------------
# Zadani
m_para   := 8:        # kg vyrobene pary z 1 kg uhli (puvodni stav)
t_1      := 40:       # degC, teplota napajeci vody
t_2      := 188:      # degC, teplota syte pary pri 1.2 MPa (tabulky)
cp_voda  := 4.245:    # kJ/(kg K), voda pri (40+188)/2 = 114 degC
dh_lv_2  := 1985.6:   # kJ/kg, vyparna entalpie pri 188 degC
# Novy stav: voda 10 degC, para 1.6 MPa
t_1n     := 10:       # degC
t_2n     := 201:      # degC, syta para pri 1.6 MPa
cp_voda_n:= 4.223:    # kJ/(kg K), pri (201+10)/2 = 106 degC
dh_lv_2n := 1935.9:   # kJ/kg, vyparna entalpie pri 201 degC

# 1. Merne entalpie (ref. stav kapalna voda pri t_1, tj. h_1 = 0)
h_1 := 0:
h_2 := cp_voda*(t_2 - t_1) + dh_lv_2;          # kJ/kg
# 2. Teplo predane v generatoru
Q_a := m_para*(h_2 - h_1);                      # kJ
# 3. Nove mnozstvi pary (ref. stav voda pri t_1n)
h_2n := cp_voda_n*(t_2n - t_1n) + dh_lv_2n;     # kJ/kg
m_para_n := Q_a/(h_2n - 0);                     # kg

# ---------------- b) kotel, uplne spaleni uhliku ----------------
# Zadani
m_uhli   := 1:        # kg uhli (cisty uhlik)
M_C      := 12e-3:    # kg/mol
prebytek := 0.50:     # 50 % prebytek vzduchu
x_O2_vzd := 0.21:     # molarni zlomek O2 ve vzduchu
x_N2_vzd := 0.79:
t_3      := 25:       # degC, uhli
t_4      := 25:       # degC, vzduch
t_5      := 500:      # degC, spaliny (= ref. teplota)
t_tab    := 25:       # degC, tabelovana teplota
dh_f_CO2 := -393.8e3: # J/mol
# Stredni molarni tepelne kapacity pri (25+500)/2 = 263 degC [J/(mol K)]
cp_O2 := 29.51:  cp_N2 := 29.78:  cp_C := 8.517:  cp_CO2 := 44.98:

# 1. Latkova mnozstvi
n_3 := m_uhli/M_C;                              # mol C
n_O2_teor := n_3:                               # C + O2 -> CO2
n_4_teor  := n_O2_teor/x_O2_vzd:
n_4 := (1 + prebytek)*n_4_teor;                 # mol vzduchu
xi  := n_3;                                     # rozsah reakce (konverze 1)

# 2. Reakcni entalpie pri 500 degC (Kirchhoff)
dh_r_tab := dh_f_CO2:                           # J/mol
dh_r_5 := dh_r_tab + (-cp_O2 - cp_C + cp_CO2)*(t_5 - t_tab);   # J/mol

# 3. Entalpicka bilance kotle (T_ref = t_5)
Q_b := n_3*cp_C*(t_3 - t_5) + n_4*(x_O2_vzd*cp_O2 + x_N2_vzd*cp_N2)*(t_4 - t_5) + xi*(-dh_r_5);  # J
# 4. Mnozstvi pary (stejne h_2 jako v a))
m_para_b := (Q_b/1000)/(h_2 - h_1);             # kg

printf("a) Q = %.0f kJ, m_para_nova = %.2f kg\n", Q_a, m_para_n);
printf("b) Q = %.2f MJ, m_para = %.2f kg\n", Q_b/1e6, m_para_b);

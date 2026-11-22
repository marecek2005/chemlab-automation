# ==============================================================================
# U14.8 Entalpicka bilance rektifikacni kolony (metanol - voda)
# ChI II - Tema 1: Bilance
# Ocekavany vysledek: m_D = 1010.64 kg, m_W = 1489.36 kg, Q_1 = 2.926e9 J,
#   chladici voda m_CH = 35.0 t, Q_3 = 5.236e8 J (m_P3 = 242.0 kg),
#   Q_2 = 3.006e9 J (m_P2 = 1389.2 kg), para celkem m_P = 1631 kg (~1640 kg)
# Pozn.: v oficialnim PDF je v souctu preklep 186.5 kg misto 242.0 kg pro m_P3,
#   vysledek 1631.17 kg je ale spravne.
# ==============================================================================
restart;

# Zadani
m_F      := 2500:        # kg, hmotnost nastriku (suroviny)
w_A_F    := 0.40:        # hm. zlomek metanolu v nastriku
w_A_D    := 0.96:        # hm. zlomek metanolu v destilatu
w_A_W    := 0.02:        # hm. zlomek metanolu ve zbytku
R_reflux := 1.5:         # pomer zpetneho toku L0/D
t_F_vstup:= 20.0:        # degC, teplota nastriku pred predehrevem
cp_A     := 2590:        # J/(kg K), metanol (kapalina)
cp_B     := 4180:        # J/(kg K), voda (kapalina)
cp_CH    := 4180:        # J/(kg K), chladici voda
dt_CH    := 20:          # K, ohrev chladici vody
# Tabulkova data
t_F      := 79.1:        # degC, teplota varu nastriku (rovnovaha k-p)
t_D      := 65.55:       # degC, teplota varu destilatu
t_W      := 97.85:       # degC, teplota varu zbytku
dh_lv_para := 2163599.1: # J/kg, vyparna entalpie vody pri 3 bar (133.54 degC)
dh_lv_A  := 1108635:     # J/kg, vyparna entalpie metanolu pri t_D
dh_lv_B  := 2345396:     # J/kg, vyparna entalpie vody pri t_D

# 1. Hmotnostni bilance kolony
sol := solve({m_F = m_D + m_W, w_A_F*m_F = w_A_D*m_D + w_A_W*m_W}, {m_D, m_W}):
assign(sol);
m_D; m_W;

# 2. Kondenzator: Q_1 a chladici voda
dh_lv_D := w_A_D*dh_lv_A + (1 - w_A_D)*dh_lv_B;   # J/kg
m_V1    := (R_reflux + 1)*m_D;                    # kg par do kondenzatoru
Q_1     := dh_lv_D*m_V1;                          # J
m_CH    := Q_1/(cp_CH*dt_CH);                     # kg chladici vody

# 3. Predehrev nastriku: Q_3 a para m_P3 (ref. teplota t_F)
cp_F := w_A_F*cp_A + (1 - w_A_F)*cp_B:
Q_3  := m_F*cp_F*(t_F - t_F_vstup);               # J
m_P3 := Q_3/dh_lv_para;                           # kg

# 4. Varak: entalpicka bilance kolony (ref. teplota t_F -> h_F = 0)
cp_D := w_A_D*cp_A + (1 - w_A_D)*cp_B:
cp_W := w_A_W*cp_A + (1 - w_A_W)*cp_B:
h_D  := cp_D*(t_D - t_F):
h_W  := cp_W*(t_W - t_F):
Q_2  := Q_1 + m_D*h_D + m_W*h_W;                  # J
m_P2 := Q_2/dh_lv_para;                           # kg

# 5. Vysledky
m_P_celkem := m_P2 + m_P3;                        # kg topne pary
printf("m_D = %.2f kg, m_W = %.2f kg\n", m_D, m_W);
printf("chladici voda = %.2f t, para celkem = %.1f kg\n", m_CH/1000, m_P_celkem);

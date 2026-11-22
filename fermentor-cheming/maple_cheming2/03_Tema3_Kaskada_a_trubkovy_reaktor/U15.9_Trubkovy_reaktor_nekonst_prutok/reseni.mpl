# ==============================================================================
# U15.9 Trubkovy reaktor, nekonstantni objemovy prutok (plynna faze)
#   SO2Cl2 -> SO2 + Cl2  (1. rad, isotermne, isobarne)
# ChI II - Tema 3: Kaskada a trubkovy reaktor
# Ocekavany vysledek: V = 8.46 m3 (oficialni reseni 8.47 m3, zadani 8.43 m3 -
#   rozdil jen zaokrouhlenim)
# ==============================================================================
restart;

# Zadani
m_dot_A0 := 50/3600:     # kg/s SO2Cl2 (50 kg/h)
M_A      := 0.13497:     # kg/mol
T        := 593.15:      # K (320 degC)
p        := 0.101e6:     # Pa
k        := 2.2e-3:      # 1/s
zeta     := 0.90:        # konverze
R_g      := 8.314:       # J/(mol K)

# 1. Vstupni latkovy tok
n_dot_A0 := m_dot_A0/M_A;                         # mol/s

# 2. Objemovy prutok roste s konverzi (n_celk = n_A0*(1 + zeta)):
#    V_dot = n_dot_A0*(1 + z)*R*T/p,  c_A = n_dot_A0*(1 - z)/V_dot
c_A := z -> p*(1 - z)/(R_g*T*(1 + z)):
# 3. dV = n_dot_A0 dz / (k*c_A)
V_R := evalf(n_dot_A0/k*int(1/c_A(z), z = 0 .. zeta));          # m3
# analyticky tvar: V = n_A0*R*T/(p*k) * (-zeta + 2*ln(1/(1 - zeta)))
V_anal := n_dot_A0*R_g*T/(p*k)*(-zeta + 2*ln(1/(1 - zeta)));

printf("n_A0 = %.4f mol/s,  V = %.2f m3\n", n_dot_A0, V_R);

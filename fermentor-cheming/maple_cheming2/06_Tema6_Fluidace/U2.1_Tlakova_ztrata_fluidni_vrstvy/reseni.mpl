# ==============================================================================
# U2.1 Tlakova ztrata fluidni vrstvy
# ChI II - Tema 6: Fluidace
# Ocekavany vysledek: Delta_p = 437.2 Pa (vztlak plynu zanedbatelny: 437.1 Pa)
# ==============================================================================
restart;

# Zadani
m_p   := 0.350:     # kg castic (350 g)
D     := 0.100:     # m, prumer kolony
rho_p := 3610:      # kg/m3
rho   := 0.641:     # kg/m3, plyn (vliv vztlaku je zanedbatelny)
g     := 9.81:      # m/s2

# 1. Prurez kolony
S := evalf(Pi*D^2/4);                       # m2
# 2. Ve fluidni vrstve tlakova sila nese tihu castic zmensenou o vztlak:
#    Delta_p = V_p*(rho_p - rho)*g/S,  V_p = m_p/rho_p
V_p := m_p/rho_p;                           # m3
Delta_p := V_p*(rho_p - rho)*g/S;           # Pa
Delta_p_zjedn := m_p*g/S;                   # Pa, bez vztlaku (oficialni vysledek)

printf("Delta_p = %.2f Pa (bez vztlaku %.2f Pa)\n", Delta_p, Delta_p_zjedn);

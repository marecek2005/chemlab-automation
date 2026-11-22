# ==============================================================================
# U1.3 Prumer kontinualniho usazovaku (Stokesova oblast)
# ChI II - Tema 5: Usazovani a odstredivky
# Ocekavany vysledek: v_u = 1.30e-3 m/s, S = 20.9 m2, D_teor = 5.15 m, D_skut = 6.9 m
# ==============================================================================
restart;

# Zadani
m_dot_S := 120*1000/3600:   # kg/s suspenze (120 t/h)
w_S     := 0.065:           # hm. zlomek pevne faze v suspenzi
w_K     := 1 - 0.65:        # hm. zlomek pevne faze v kalu (kal ma 65 % vody)
d_p     := 40e-6:           # m
rho_p   := 2700:            # kg/m3
rho     := 999.09:          # kg/m3, voda
eta     := 1.138e-3:        # Pa s
g       := 9.81:            # m/s2

# 1. Bilance: kal a cira kapalina (preliv)
m_dot_K := m_dot_S*w_S/w_K;            # kg/s
m_dot_F := m_dot_S - m_dot_K;          # kg/s
V_dot_F := m_dot_F/rho;                # m3/s

# 2. Kontrola oblasti (Ar < 3.6 -> Stokes) a usazovaci rychlost
Ar  := g*d_p^3*rho*(rho_p - rho)/eta^2;
v_u := g*d_p^2*(rho_p - rho)/(18*eta);  # m/s
Re  := v_u*d_p*rho/eta;                 # kontrola < 0.2

# 3. Plocha a prumer usazovaku (skutecny = 4/3 teoretickeho)
S_us   := V_dot_F/v_u;                  # m2
D_teor := evalf(sqrt(4*S_us/Pi));       # m
D_skut := 4/3*D_teor;                   # m

printf("Ar = %.3f, v_u = %.4e m/s, S = %.2f m2, D_skut = %.2f m\n", Ar, v_u, S_us, D_skut);

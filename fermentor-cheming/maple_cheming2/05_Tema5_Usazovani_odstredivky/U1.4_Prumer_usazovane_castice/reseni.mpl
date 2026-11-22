# ==============================================================================
# U1.4 Nejmensi prumer castice zachycene v usazovaku (Stokes)
# ChI II - Tema 5: Usazovani a odstredivky
# Ocekavany vysledek: v_u = 1.415e-4 m/s, d_p = 13.15 um
# ==============================================================================
restart;

# Zadani
m_dot_S := 2*1000/3600:   # kg/s suspenze (2 t/h)
w_S     := 0.10:          # hm. zlomek pevne faze v suspenzi
w_K     := 0.50:          # hm. zlomek pevne faze v kalu
D_us    := 2:             # m, prumer usazovaku
rho_p   := 2500:          # kg/m3
rho     := 1000:          # kg/m3
eta     := 1e-3:          # Pa s
g       := 9.81:          # m/s2

# 1. Bilance: cira kapalina (preliv)
m_dot_K := m_dot_S*w_S/w_K;
m_dot_F := m_dot_S - m_dot_K;          # kg/s
V_dot_F := m_dot_F/rho;                # m3/s

# 2. Rychlost stoupani kapaliny = usazovaci rychlost nejmensi zachycene castice
S_us := evalf(Pi*D_us^2/4);            # m2
v_u  := V_dot_F/S_us;                  # m/s

# 3. Stokesuv vztah -> prumer castice, kontrola Re
d_p := sqrt(18*eta*v_u/(g*(rho_p - rho)));     # m
Re  := v_u*d_p*rho/eta;                        # << 0.2 -> Stokes plati
d_p_um := d_p*1e6;                             # um

printf("v_u = %.4e m/s, d_p = %.2f um, Re = %.2e\n", v_u, d_p_um, Re);

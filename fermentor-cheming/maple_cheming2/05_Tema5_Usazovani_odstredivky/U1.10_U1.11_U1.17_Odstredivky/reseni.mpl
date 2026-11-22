# ==============================================================================
# U1.10, U1.11, U1.17 Odstredivky - usazovani kvasnicnych bunek
# ChI II - Tema 5: Usazovani a odstredivky
# Ocekavany vysledek:
#   U1.10: v_ug = 4.54e-7 m/s; 5000 min-1: Ar = 0.0761, v_uo = 1.27e-3 m/s, K_u = 2.8e3;
#          10000 min-1: Ar = 0.305, v_uo = 5.08e-3 m/s, K_u = 1.12e4;
#          50000 min-1: Ar = 7.6 (Allen), v_uo = 0.183 m/s, K_u = 4.03e5
#   U1.11: tau = 86.6 s, kontinualne V_dot = 7.25e-4 m3/s = 2.61 m3/h,
#          vsadkove V_dot = 0.237 m3/h
#   U1.17: v_ug = 2e-7 m/s, Sigma_c = 833 m2
# Pozn.: oficialni PDF v U1.11 uvadi omylem Ar1 = 0.107 (spravne 0.0761, pro R = 0.15 m
#   pak Ar = 0.114); na zaver (Stokesova oblast) to nema vliv.
# ==============================================================================
restart;

# ---------------- U1.10 ----------------
# Zadani
d_p   := 5e-6:        # m
rho_p := 1050:        # kg/m3, bunky
rho   := 1000:        # kg/m3, medium
eta   := 1.5e-3:      # Pa s
g     := 9.81:        # m/s2
r_rot := 0.100:       # m, polomer rotace
n_ot  := [5000, 10000, 50000]/60:   # 1/s

# 1. Gravitacni usazovani (Ar < 3.6 -> Stokes)
Ar_g := g*d_p^3*rho*(rho_p - rho)/eta^2;
v_ug := d_p^2*g*(rho_p - rho)/(18*eta);              # m/s

# 2. Odstredive pole: g nahradime a_c = (2*Pi*n)^2*r
for j from 1 to 3 do
  a_c := evalf((2*Pi*n_ot[j])^2*r_rot);
  Ar  := d_p^3*rho*(rho_p - rho)*a_c/eta^2;
  if Ar < 3.6 then      # Stokesova oblast
    v_uo := d_p^2*(rho_p - rho)*a_c/(18*eta);
  else                  # prechodna (Allenova) oblast
    v_uo := 0.153*d_p^1.14*(rho_p - rho)^0.71/(rho^0.29*eta^0.43)*a_c^0.71;
  end if;
  K_u := v_uo/v_ug;     # faktor urychleni
  printf("n = %6.0f min-1: Ar = %.4g, v_uo = %.4g m/s, K_u = %.4g\n", 60*n_ot[j], Ar, v_uo, K_u);
end do:

# ---------------- U1.11 ----------------
# Zadani
L_odst := 1:          # m, delka trubkove odstredivky
R_odst := 0.15:       # m, vnitrni polomer plaste
r_0    := 0.05:       # m, polomer hladiny
n_1    := 5000/60:    # 1/s

# 1. Kontrola oblasti pri maximalnim polomeru R
Ar_R := evalf(d_p^3*rho*(rho_p - rho)*(2*Pi*n_1)^2*R_odst/eta^2);   # < 3.6 -> Stokes
# 2. Doba usazovani: tau = int(dr/v_uo, r = r_0..R)
tau_us := evalf(18*eta/(d_p^2*(rho_p - rho)*(2*Pi*n_1)^2)*ln(R_odst/r_0));   # s
# 3. Kontinualni provoz: V_dot = V/tau
V_prac := evalf(Pi*(R_odst^2 - r_0^2)*L_odst);     # m3
V_dot_kont := V_prac/tau_us;                       # m3/s
V_dot_kont_h := 3600*V_dot_kont;                   # m3/h
# 4. Vsadkovy provoz: tau_c = 3 tau + tau + 7 tau
tau_c := 11*tau_us;                                # s
N_c   := 3600/tau_c;                               # cyklu za hodinu
V_dot_vsad_h := V_prac*N_c;                        # m3/h
printf("U1.11: tau = %.1f s, kont. %.3f m3/h, vsadk. %.3f m3/h\n", tau_us, V_dot_kont_h, V_dot_vsad_h);

# ---------------- U1.17 ----------------
# Zadani
V_dot_po := 10e-3/60:    # m3/s (10 dm3/min)
K_u_lab  := 500:         # faktor urychleni laboratorni odstredivky
v_uo_lab := 100e-6:      # m/s
# 1. Gravitacni usazovaci rychlost a faktor Sigma_c
v_ug_17 := v_uo_lab/K_u_lab;          # m/s
Sigma_c := V_dot_po/v_ug_17;          # m2
printf("U1.17: v_ug = %.2e m/s, Sigma_c = %.0f m2\n", v_ug_17, Sigma_c);

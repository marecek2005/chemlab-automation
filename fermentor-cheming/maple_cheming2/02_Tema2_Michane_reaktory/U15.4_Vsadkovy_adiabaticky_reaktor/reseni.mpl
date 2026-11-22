# ==============================================================================
# U15.4 Adiabaticky vsadkovy michany reaktor  A + B -> C + D
# ChI II - Tema 2: Michane reaktory
# Ocekavany vysledek: T(zeta = 0.4) = 393.2 K > 373 K -> adiabaticky provoz NELZE
# ==============================================================================
restart;

# Zadani
T_0   := 313:          # K, pocatecni teplota
c_A0  := 2.4e3:        # mol/m3 (2.4 kmol/m3)
rho   := 960:          # kg/m3
dh_r  := -167.6e3:     # J/mol
cp    := 2090:         # J/(kg K)
zeta  := 0.40:         # konverze A
T_max := 373:          # K, povolena teplota
# (doba 4.7 h k vysledku teploty neni potreba)

# 1. Latkova bilance:  d c_A/d tau = -r
# 2. Entalpicka bilance: rho*cp*dT/d tau = r*(-dh_r)
# 3. Podelenim:  dT/d c_A = dh_r/(rho*cp)  -> integrace od c_A0 do c_A
c_A_konec := c_A0*(1 - zeta);                    # mol/m3
ode := diff(T(c), c) = dh_r/(rho*cp):
sol := dsolve({ode, T(c_A0) = T_0}, T(c)):
T_konec := evalf(eval(rhs(sol), c = c_A_konec));  # K
# kontrola integralnim tvarem:
T_konec_int := T_0 + (-dh_r)*c_A0*zeta/(rho*cp);

if T_konec > T_max then
  printf("T = %.1f K > %d K -> reaktor NELZE provozovat adiabaticky\n", T_konec, T_max);
else
  printf("T = %.1f K <= %d K -> adiabaticky provoz je mozny\n", T_konec, T_max);
end if;

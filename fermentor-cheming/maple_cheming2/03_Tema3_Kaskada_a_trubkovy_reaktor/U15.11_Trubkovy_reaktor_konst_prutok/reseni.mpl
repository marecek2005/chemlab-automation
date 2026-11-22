# ==============================================================================
# U15.11 Trubkovy reaktor s pistovym tokem, konstantni prutok, A -> B (1. rad)
# ChI II - Tema 3: Kaskada a trubkovy reaktor
# Ocekavany vysledek: V = 100.1 dm3 (~100 dm3), pri dvojnasobne delce zeta = 0.99
# ==============================================================================
restart;

# Zadani
V_dot := 10:        # dm3/min
k     := 0.23:      # 1/min
zeta  := 0.90:      # c_A,L = 0.1*c_A0

# 1. Diferencialni bilance: dV = n_dot_A0 * d zeta / r,  r = k*c_A = k*c_A0*(1 - zeta)
#    => V = V_dot/k * int(1/(1 - z), z = 0 .. zeta)
V_R := evalf(V_dot/k*int(1/(1 - z), z = 0 .. zeta));    # dm3

# 2. Dvojnasobna delka -> dvojnasobny objem
V_2 := 2*V_R:
zeta_2 := fsolve(V_2 = V_dot/k*(-ln(1 - z)), z = 0 .. 0.99999);

printf("V = %.1f dm3,  zeta(2L) = %.4f\n", V_R, zeta_2);

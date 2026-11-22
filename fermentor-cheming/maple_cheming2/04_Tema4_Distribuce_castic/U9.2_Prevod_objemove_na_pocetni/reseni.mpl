# ==============================================================================
# U9.2 Sitova analyza mocoviny - prevod objemove distribuce na pocetni
# ChI II - Tema 4: Distribuce castic
# Ocekavany vysledek: dF3 = 0.0896; 0.194; 0.260; 0.457, dF0 = 0.787; 0.123; 0.058; 0.032,
#   x10 = 0.720 mm, x32 = 1.479 mm, x43 = 1.861 mm, x30 = 1.032 mm,
#   pocet castic ve 100 g ~ 1.32e5
# ==============================================================================
restart;

# Zadani
x_hran := [0, 1.0, 1.4, 2.0, 3.0]:     # mm, hranice trid (dno, sita, max. velikost)
m_frak := [3.0, 6.5, 8.7, 15.3]:       # g, hmotnost frakci (od nejmensi)
rho_p  := 1320:                        # kg/m3
m_vzorek := 0.100:                     # kg (100 g)
n := nops(m_frak):

# 1. Stredy a sirky trid
x_i  := [seq((x_hran[i] + x_hran[i+1])/2, i = 1 .. n)];    # mm
dx_i := [seq(x_hran[i+1] - x_hran[i], i = 1 .. n)];        # mm

# 2. a) Objemova (hmotnostni) distribuce
dF3 := [seq(m_frak[i]/add(m_frak[j], j = 1 .. n), i = 1 .. n)];
F3  := [0, seq(add(dF3[j], j = 1 .. i), i = 1 .. n)];      # na hranicich trid
f3  := [seq(dF3[i]/dx_i[i], i = 1 .. n)];                  # 1/mm

# 3. b) Prevod na pocetni distribuci: dF0_i ~ dF3_i / x_i^3
suma := add(dF3[j]/x_i[j]^3, j = 1 .. n):
dF0 := [seq(dF3[i]/x_i[i]^3/suma, i = 1 .. n)];
F0  := [0, seq(add(dF0[j], j = 1 .. i), i = 1 .. n)];
f0  := [seq(dF0[i]/dx_i[i], i = 1 .. n)];                  # 1/mm

# 4. c) Momenty pocetni distribuce a stredni velikosti
M := kk -> add(x_i[i]^kk*dF0[i], i = 1 .. n):
x10 := M(1)/M(0);              # mm
x32 := M(3)/M(2);              # mm
x43 := M(4)/M(3);              # mm

# 5. d) Pocet castic ve 100 g (stredni objem castice ~ pi/6*x30^3)
x30 := (M(3)/M(0))^(1/3);                      # mm
m_castice := rho_p*Pi/6*(x30*1e-3)^3;          # kg
N_castic := evalf(m_vzorek/m_castice);

printf("x10 = %.3f, x32 = %.3f, x43 = %.3f mm, N(100 g) = %.4g\n", x10, x32, x43, N_castic);

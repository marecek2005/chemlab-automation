# ==============================================================================
# U2.2 Prahova rychlost fluidace
# ChI II - Tema 6: Fluidace
# Ocekavany vysledek: Ar = 2.69e6, Re_P0 = 288.7, v_0 = 1.17 m/s
# ==============================================================================
restart;

# Zadani
d_p   := 4e-3:       # m
rho_p := 1280:       # kg/m3
eps_0 := 0.40:       # mezerovitost nehybne vrstvy
g     := 9.81:       # m/s2
rho   := 1.1455:     # kg/m3, vzduch 25 degC, 98 kPa
nu    := 16.15e-6:   # m2/s, kinematicka viskozita vzduchu

# 1. Archimedovo kriterium (oficialne s rho_p - rho ~ rho_p, rozdil zanedbatelny)
Ar := g*d_p^3*(rho_p - rho)/(nu^2*rho);
# 2. Reynoldsovo kriterium na prahu fluidace (vztah 2.20)
Re_P0 := 42.628*(1 - eps_0)*(sqrt(1 + 3.1357e-4*eps_0^3/(1 - eps_0)^2*Ar) - 1);
# 3. Prahova rychlost
v_0 := Re_P0*nu/d_p;             # m/s

printf("Ar = %.0f, Re_P0 = %.1f, v_0 = %.3f m/s\n", Ar, Re_P0, v_0);

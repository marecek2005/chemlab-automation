# ==============================================================================
# U2.5 Prutok kapaliny expandovanou fluidni vrstvou
# ChI II - Tema 6: Fluidace
# Ocekavany vysledek: Ar = 72144, Re = 152.2, v = 0.0711 m/s, m_dot = 405 kg/h
# ==============================================================================
restart;

# Zadani
d_p   := 0.68e-3:    # m
D     := 0.04:       # m, prumer trubky
rho_p := 4230:       # kg/m3, katalyzator
rho   := 1260:       # kg/m3, kapalina
eta   := 0.0004:     # Pa s
g     := 9.81:       # m/s2
eps   := 1 - 0.30:   # mezerovitost (30 obj. % pevne faze)

# 1. Prurez trubky
S := evalf(Pi*D^2/4);                           # m2
# 2. Archimedovo kriterium
Ar := g*d_p^3*rho*(rho_p - rho)/eta^2;
# 3. Reynoldsovo kriterium expandovane vrstvy (vztah 2.39)
Ar_eps := Ar*eps^4.75:
Re := Ar_eps/(18 + 0.6*sqrt(Ar_eps));
# 4. Rychlost a hmotnostni prutok
v := Re*eta/(rho*d_p);                          # m/s
m_dot := v*S*rho*3600;                          # kg/h

printf("Ar = %.0f, Re = %.2f, v = %.5f m/s, m_dot = %.0f kg/h\n", Ar, Re, v, m_dot);

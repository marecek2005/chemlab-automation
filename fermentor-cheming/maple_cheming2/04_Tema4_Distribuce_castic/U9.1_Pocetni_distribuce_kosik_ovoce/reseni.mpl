# ==============================================================================
# U9.1 Pocetni distribuce "castic" - kosik ovoce
# ChI II - Tema 4: Distribuce castic
# Ocekavany vysledek: N = 136, L = 200 cm, S = 3970.9 cm2, V = 14855.1 cm3,
#   x10 = 1.4706 cm, x30 = 5.9308 cm, x32 = 22.4456 cm, x43 = 28.7968 cm
# ==============================================================================
restart;

# Zadani: meloun, broskev, tresen, rybiz
x_i := [30, 6, 2, 0.8]:       # cm, prumery
N_i := [1, 5, 30, 100]:       # ks
n   := nops(x_i):

# 1. a) Celkovy pocet, delka, povrch a objem (kulove castice)
N_celk := add(N_i[i], i = 1 .. n);
L_celk := add(N_i[i]*x_i[i], i = 1 .. n);                    # cm
S_celk := evalf(add(N_i[i]*Pi*x_i[i]^2, i = 1 .. n));        # cm2
V_celk := evalf(add(N_i[i]*Pi/6*x_i[i]^3, i = 1 .. n));      # cm3

# 2. Pocetni relativni cetnosti a momenty M_k = sum x_i^k * dF0_i
dF0 := [seq(N_i[i]/N_celk, i = 1 .. n)]:
M := kk -> evalf(add(x_i[i]^kk*dF0[i], i = 1 .. n)):

# 3. b) Stredni velikosti
x10 := M(1)/M(0);
x30 := (M(3)/M(0))^(1/3);
x32 := M(3)/M(2);
x43 := M(4)/M(3);

# 4. c) Kontrola vztahu
L_celk/N_celk - x10;                     # = 0
V_celk/N_celk - Pi/6*x30^3;              # = 0
S_celk/V_celk - 6/x32;                   # = 0

printf("x10 = %.4f, x30 = %.4f, x32 = %.4f, x43 = %.4f cm\n", x10, x30, x32, x43);

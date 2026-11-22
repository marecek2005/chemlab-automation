# ==============================================================================
# U9.7 Parametry lognormalni distribuce - aerosol kapicek (fit nejmensimi ctverci)
# ChI II - Tema 4: Distribuce castic
# Ocekavany vysledek: mu = 1.80, sigma^2 = 0.072, mu_LN = 6.27 um, sigma_LN^2 = 2.93 um2,
#   x10 = 6.27 um, x20 = 6.50 um, x20^2 - x10^2 = sigma_LN^2
# ==============================================================================
restart;
with(Optimization):

# Zadani: velikost kapky x [um] a pocetni hustota pravdepodobnosti f0 [1/um]
x_data := [2.46, 3.55, 4.54, 5.62, 6.58, 7.30, 9.21, 14.51, 19.48]:
f_data := [0.008, 0.082, 0.191, 0.251, 0.232, 0.184, 0.046, 0.005, 0.0003]:
n_bodu := nops(x_data):

# 1. a) Model lognormalni hustoty a soucet ctvercu odchylek
f_mod := (x, mu, s2) -> 1/(x*sqrt(2*Pi*s2))*exp(-(ln(x) - mu)^2/(2*s2)):
S_ctv := add((f_data[i] - f_mod(x_data[i], mu, s2))^2, i = 1 .. n_bodu):
sol_fit := NLPSolve(S_ctv, initialpoint = {mu = 1.8, s2 = 0.07}, assume = nonnegative);
mu_opt := eval(mu, sol_fit[2]);      # ~1.80
s2_opt := eval(s2, sol_fit[2]);      # ~0.072

# 2. b) Stredni hodnota a rozptyl lognormalniho rozdeleni
mu_LN := exp(mu_opt + s2_opt/2);                        # um
s2_LN := (exp(s2_opt) - 1)*exp(2*mu_opt + s2_opt);      # um2

# 3. c) Prumery pres momenty M_k = exp(k*mu + k^2*s2/2)
M := (kk, mu, s2) -> exp(kk*mu + kk^2*s2/2):
x10 := M(1, mu_opt, s2_opt);         # um
x20 := sqrt(M(2, mu_opt, s2_opt));   # um

# 4. d) Overeni sigma_LN^2 = x20^2 - x10^2
rozdil := x20^2 - x10^2 - s2_LN;     # ~0

printf("mu = %.4f, s2 = %.4f, mu_LN = %.2f um, s2_LN = %.2f um2, x10 = %.2f, x20 = %.2f um\n",
       mu_opt, s2_opt, mu_LN, s2_LN, x10, x20);

# ==============================================================================
# U9.4 Vymena katalyzatoru - lognormalni distribuce, Sauteruv prumer
# ChI II - Tema 4: Distribuce castic
# Ocekavany vysledek: x32 stary = 10.97 um, novy = 17.55 um;
#   celkovy povrch klesne na 62.5 %, pocet castic na 24.3 %
# ==============================================================================
restart;

# Zadani (pocetni lognormalni distribuce, x v um), stejna hmotnost naplne
mu_stary := 2.043:  s2_stary := 0.1408:
mu_novy  := 2.517:  s2_novy  := 0.1392:

# 1. k-ty moment lognormalni distribuce
M := (kk, mu, s2) -> exp(kk*mu + kk^2*s2/2):

# 2. Momenty M2, M3
M2_stary := M(2, mu_stary, s2_stary);   # 78.85 um2
M3_stary := M(3, mu_stary, s2_stary);   # 864.9 um3
M2_novy  := M(2, mu_novy, s2_novy);     # 202.8 um2
M3_novy  := M(3, mu_novy, s2_novy);     # 3559.6 um3

# 3. Sauteruv prumer x32 = M3/M2
x32_stary := M3_stary/M2_stary;
x32_novy  := M3_novy/M2_novy;

# 4. Pri stejne hmotnosti (objemu) V: S = 6V/x32, N = V/(pi/6*M3)
pomer_povrchu := x32_stary/x32_novy;
pomer_poctu   := M3_stary/M3_novy;

printf("x32: %.2f -> %.2f um, povrch %.1f %%, pocet %.1f %%\n",
       x32_stary, x32_novy, 100*pomer_povrchu, 100*pomer_poctu);

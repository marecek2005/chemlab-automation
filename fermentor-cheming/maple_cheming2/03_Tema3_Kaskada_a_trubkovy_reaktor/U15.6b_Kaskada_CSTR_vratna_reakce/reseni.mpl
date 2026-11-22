# ==============================================================================
# U15.6b Kaskada idealne michanych reaktoru, vratna reakce 2A <-> B + C
# ChI II - Tema 3: Kaskada a trubkovy reaktor
# Ocekavany vysledek: c_A1..c_A4 = 0.9437; 0.6692; 0.5133; 0.4161 kmol/m3
#   -> c_A4 <= 0.4333 kmol/m3, potrebny pocet reaktoru N = 4
# ==============================================================================
restart;

# Zadani
c_A0   := 1.5:          # kmol/m3, vstupni koncentrace A
k      := 5:            # m3/(kmol h), rychlostni konstanta prime reakce
K_C    := 16:           # rovnovazna konstanta
tau    := 6.28/100:     # h, doba zdrzeni v jednom reaktoru
zeta   := 0.71111:      # pozadovana konverze
c_A_cil := c_A0*(1 - zeta);          # kmol/m3 (= 0.4333)

# 1. Rychlost reakce (c_B = c_C = (c_A0 - c_A)/2)
r := cA -> k*(cA^2 - ((c_A0 - cA)/2)^2/K_C):

# 2. Bilance A v k-tem reaktoru: c_vstup - c_A = 2*r(c_A)*tau  (nu_A = -2)
# 3. Postupne reaktor po reaktoru, dokud c_A <= c_A_cil
c_vstup := c_A0:
for N from 1 to 20 do
  c_vystup := fsolve(c_vstup - cA = 2*r(cA)*tau, cA = 0 .. c_vstup);
  printf("Reaktor %d: c_A = %.4f kmol/m3\n", N, c_vystup);
  if c_vystup <= c_A_cil then break; end if;
  c_vstup := c_vystup;
end do:

# 4. Vysledek
printf("Potrebny pocet reaktoru N = %d\n", N);

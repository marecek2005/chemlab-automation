# ==============================================================================
# U15.16 Neizotermni kaskada 4 CSTR (ruzne teploty -> ruzne k), reakce 1. radu A -> B
# ChI II - Tema 3: Kaskada a trubkovy reaktor
# Ocekavany vysledek: a) tau = 358.7 s, V = 0.599 m3 (~0.6 m3) kazdy reaktor
#   b) pri 288 K (k_2): N = 6.13 -> 7 reaktoru
# Pozn.: oficialni reseni ve "Vysledku" uvadi "sest", jeho vlastni vypocet ale dava
#   c_A6 = 0.0851 > 0.081 kmol/m3, takze spravne je 7 reaktoru.
# ==============================================================================
restart;

# Zadani
c_A0  := 0.9:            # kmol/m3
zeta  := 0.91:           # pozadovana konverze
V_dot := 1.67e-3:        # m3/s
k_1 := 0.96e-3:  k_2 := 1.34e-3:  k_3 := 2.63e-3:  k_4 := 5.22e-3:   # 1/s
c_A4  := c_A0*(1 - zeta);            # kmol/m3 (= 0.081)

# 1. a) Bilance kazdeho reaktoru (stejny objem -> stejne tau)
rov_1 := c_A0 - c_A1 = k_1*c_A1*tau:
rov_2 := c_A1 - c_A2 = k_2*c_A2*tau:
rov_3 := c_A2 - c_A3 = k_3*c_A3*tau:
rov_4 := c_A3 - c_A4 = k_4*c_A4*tau:
sol := fsolve({rov_1, rov_2, rov_3, rov_4}, {c_A1, c_A2, c_A3, tau = 0 .. 10000});
tau_a := eval(tau, sol);             # s
V_R   := tau_a*V_dot;                # m3

# 2. b) Vsechny reaktory pri 288 K (k_2), stejny objem V_R
#    c_A,N = c_A0/(1 + k_2*tau)^N
N_presne := fsolve(c_A4 = c_A0/(1 + k_2*tau_a)^N, N);
N_reaktoru := ceil(N_presne);
c_A6 := c_A0/(1 + k_2*tau_a)^6;      # kontrola: 6 reaktoru nestaci

printf("a) tau = %.2f s, V = %.3f m3\n", tau_a, V_R);
printf("b) N = %.3f -> %d reaktoru (c_A6 = %.4f > %.3f)\n", N_presne, N_reaktoru, c_A6, c_A4);

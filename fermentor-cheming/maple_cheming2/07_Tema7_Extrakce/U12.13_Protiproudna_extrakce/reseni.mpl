# ==============================================================================
# U12.13 Protiproudna extrakce v kolone s vyplni: voda - kys. octova - diethylether
# ChI II - Tema 7: Extrakce
# Ocekavany vysledek: m_S = 1.26 kg etheru na 1 kg suroviny, N = 3.60 teor. stupne,
#   vyska vyplne h = 3.60*0.75 = 2.7 m (oficialni "Vysledek" zaokrouhluje na 3 m)
# Pozn.: delky usecek a slozeni rafinatu R1-R3 jsou odecteny graficky z diagramu
#   (oficialni reseni uvadi jen w_A,R3 = 0.051 a w_A,R4 = 0.016).
# ==============================================================================
restart;

# Zadani
m_F    := 1.0:     # kg suroviny
w_A_F  := 0.30:    # kys. octova v surovine
w_A_N  := 0.03:    # pozadovany zlomek A v rafinatu R_N
u_A_1  := 0.17:    # zlomek A v extraktu E_1
H_EPT  := 0.75:    # m, vyska ekvivalentni rovnovaznemu stupni

# 1. Spotreba etheru (pakove pravidlo v bode M = prusecik F-S a E1-R_N)
FM := 16.9:  MS := 13.4:          # cm, odecteno z diagramu
m_S := m_F*FM/MS;                 # kg

# 2. Krokovani stupnu pres pol P a konody (odecteno z diagramu)
w_A_R := [0.174, 0.098, 0.051, 0.016]:
n := 4:                            # w_A_R4 < w_A_N
# 3. Interpolace neceleho stupne: N = n - 1 + (w_A_N - w_A,n-1)/(w_A,n - w_A,n-1)
N_teor := n - 1 + (w_A_N - w_A_R[n-1])/(w_A_R[n] - w_A_R[n-1]);

# 4. Vyska vyplne
h := N_teor*H_EPT;                 # m
h_cela_patra := ceil(N_teor)*H_EPT;  # m

printf("m_S = %.3f kg, N = %.2f, h = %.2f m (%.2f m na cela patra)\n", m_S, N_teor, h, h_cela_patra);

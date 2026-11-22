# ==============================================================================
# U12.15 Opakovana (krizova) extrakce: voda - kyselina octova - diethylether, 25 degC
# ChI II - Tema 7: Extrakce
# Ocekavany vysledek: 4 stupne, celkem 28 kg etheru, w_A,R4 = 0.110 <= 0.115
# Pozn.: slozeni rafinatu a delky usecek jsou odecteny graficky z trojuhelnikoveho
#   diagramu (tab. XIV-1c) podle oficialniho reseni - nelze je spocitat analyticky.
# ==============================================================================
restart;

# Zadani
m_F   := 30:       # kg suroviny
w_A_F := 0.25:     # hm. zlomek kys. octove v surovine
m_S   := 7:        # kg cisteho etheru do kazdeho stupne
w_cil := 0.115:    # max. hm. zlomek A v rafinatu posledniho stupne

# Odecteno z diagramu: w_A rafinatu a pomer usecek ME/RE pro stupne 1-3
w_A_R := [0.2055, 0.169, 0.138, 0.110]:
pomer_MERE := [146/174, 143/199, 162/219]:

# 1. Pakove pravidlo: m_R,k = (m_R,k-1 + m_S)*ME/RE, stupen po stupni
m_R := m_F:  w_A_vstup := w_A_F:
for kk from 1 to 4 do
  m_M   := m_R + m_S;                       # smesny bod M_k
  w_A_M := w_A_vstup*m_R/m_M;               # slozeni smesneho bodu
  w_A_vstup := w_A_R[kk];
  if kk <= 3 then m_R := m_M*pomer_MERE[kk]; end if;
  printf("Stupen %d: w_A,M = %.4f, w_A,R = %.4f\n", kk, w_A_M, w_A_R[kk]);
  if w_A_R[kk] <= w_cil then N_stupnu := kk; break; end if;
end do:

# 2. Vysledek
m_S_celk := N_stupnu*m_S;                   # kg
printf("N = %d stupnu, ether celkem %d kg\n", N_stupnu, m_S_celk);

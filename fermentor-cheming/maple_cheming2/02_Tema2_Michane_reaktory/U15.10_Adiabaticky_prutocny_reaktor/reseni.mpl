# ==============================================================================
# U15.10 Adiabaticky prutocny reaktor - dehydrogenace methanolu
#   CH3OH(g) -> HCHO(g) + H2(g)
# ChI II - Tema 2: Michane reaktory
# Ocekavany vysledek: dh_r(25 degC) = 85.3 kJ/mol, T_2 = 365 degC
# ==============================================================================
restart;

# Zadani (zaklad: 1 mol/s methanolu na vstupu)
n_dot_vstup := 1:        # mol/s CH3OH
T_1     := 675:          # degC, teplota vstupu
zeta    := 0.25:         # konverze methanolu
T_ref   := 25:           # degC, tabelovana teplota slucovacich entalpii
cp_MeOH := 71:           # J/(mol K)
cp_HCHO := 50:           # J/(mol K)
cp_H2   := 29:           # J/(mol K)
dh_f_MeOH := -201300:    # J/mol, slucovaci entalpie CH3OH(g) pri 25 degC
dh_f_HCHO := -116000:    # J/mol, slucovaci entalpie HCHO(g) pri 25 degC
dh_f_H2   := 0:          # J/mol

# 1. Rozsah reakce
xi := n_dot_vstup*zeta;                                  # mol/s

# 2. Reakcni entalpie pri 25 degC a zmena tepelne kapacity
dh_r_ref := dh_f_HCHO + dh_f_H2 - dh_f_MeOH;             # J/mol (endotermni)
d_cp     := cp_HCHO + cp_H2 - cp_MeOH;                   # J/(mol K)

# 3. Entalpicka bilance adiabatickeho reaktoru (ref. teplota T_2 pro proudy):
#    vstup ochladime z T_1 na T_2, reakce probiha pri T_2
#    n_dot_vstup*cp_MeOH*(T_1 - T_2) + xi*(-dh_r(T_2)) = 0
dh_r := T -> dh_r_ref + d_cp*(T - T_ref):
rov  := n_dot_vstup*cp_MeOH*(T_1 - T_2) + xi*(-dh_r(T_2)) = 0;
T_2  := fsolve(rov, T_2);                                # degC

printf("dh_r(25 degC) = %.1f kJ/mol,  T_2 = %.1f degC\n", dh_r_ref/1000, T_2);

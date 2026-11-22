import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# 1. Parametry systému
t_end = 15 * 3600  # 15 hodin v sekundách
r = 2.639e-6       # specifická respirační rychlost [mol/g/s]
x0 = 1.67          # počáteční koncentrace biomasy [g/L]
m_ = 6.67e-5       # specifická růstová rychlost [1/s]
V = 1200           # objem fermentoru [L]
R0 = x0*r

Po = 10            # příkonové číslo [-]
rho = 1005         # hustota [kg/m3]
n_rot = 1.67       # frekvence otáčení [1/s]
d = 0.4            # průměr míchadla [m]

Q_L_s = 3          # průtok vzduchu [L/s]
Q_m3_s = Q_L_s / 1000
S = np.pi * 0.88**2
R_gas = 8.314      # [J/mol/K]
T = 273.15 + 35    # [K]
p_atm = 101325     # [Pa]
xO2_in = 0.21      # molární zlomek O2 ve vzduchu

# 2. Výpočet kla a Henryho konstanty
P = Po * rho * n_rot**3 * d**5
P_aer = P * (1 - 0.45)
v_s = Q_m3_s / S

# Oprava pro kLa: standardní korelace berou specifický příkon P/V ve [W/m3]
V_m3 = V / 1000
kla = 5.8e-4 * (P_aer / V_m3)**1.2 * v_s**0.44

# Reálná Henryho konstanta pro O2 ve vodě při 35 °C (Sander, 2015)
# Hodnota: ~1.07e-8 mol/(L*Pa)
H = 1.07e-8  # [mol/L/Pa]

# 3. Definice časově závislých funkcí
def get_R(t):
    """Respirační rychlost v čase [mol/L/s]"""
    return r * x0 * np.exp(m_ * t)

def get_c_star(t):
    """Saturační koncentrace v čase [mol/L] závislá na složení odchozího plynu"""
    n_in_O2 = (p_atm * xO2_in * Q_m3_s) / (R_gas * T)  # mol/s
    n_cons_O2 = get_R(t) * V                          # mol/s
    
    # Kyslík v odchozím plynu nemůže být záporný (max spotřeba je omezena přítokem)
    n_residual_O2 = max(1e-10, n_in_O2 - n_cons_O2)
    c_star = H * n_residual_O2 * R_gas * T / Q_m3_s
    
    return c_star

# Kritická koncentrace (20 % počáteční saturační hodnoty)
c_star_0 = get_c_star(0)
c_crit = 0.2 * c_star_0

# 4. Diferenciální rovnice
def dcl_dt(t, cl):
    # ODE: dcl/dt = kla * (c*(t) - cl) - R(t)
    # Pokud je cl na nule a spotřeba je vyšší než přenos, cl se nemění
    val = kla * (get_c_star(t) - cl) - get_R(t)
    if cl <= 0 and val < 0:
        return 0
    return val

# 5. Numerické řešení
t_span = (0, t_end)
t_eval = np.linspace(0, t_end, 1000)
sol = solve_ivp(dcl_dt, t_span, [c_star_0], t_eval=t_eval, method='RK45')

cl_results = sol.y[0]
t_results = sol.t

# 6. Hledání času dosažení kritické koncentrace
idx_crit = np.where(cl_results <= c_crit)[0]
if len(idx_crit) > 0:
    t_crit = t_results[idx_crit[0]]
    print(f"Kritická koncentrace {c_crit*1000:.4f} mmol/L dosažena v čase (Solver): {t_crit/3600:.2f} h")
else:
    t_crit = None
    print("Kritická koncentrace nebyla dosažena (Solver).")

# 7. Řešení pro ustálený stav (dcL/dt = 0)
# kLa * (c*(t) - c_crit) - R(t) = 0
# c*(t) = c_star_0 - R(t) * (V * H * R_gas * T / Q_m3_s)
K_const = (V * H * R_gas * T) / Q_m3_s
R_steady = (kla * (c_star_0 - c_crit)) / (1 + kla * K_const)
t_steady = np.log(R_steady / R0) / m_
print(f"Čas pro ustálený stav (dcL/dt = 0): {t_steady/3600:.2f} h")

# 8. Vizualizace
fig, ax1 = plt.subplots(figsize=(9, 6))

ax1.plot(t_results / 3600, cl_results * 1000, 'g-', label='cl(t) - rozpuštěný O2')
c_star_t = np.array([get_c_star(ti) for ti in t_results])
ax1.plot(t_results / 3600, c_star_t * 1000, 'r--', label='c*(t) - saturační')
ax1.axhline(c_crit * 1000, color='orange', linestyle=':', label='Kritická mez (20% c*₀)')

if t_crit:
    ax1.axvline(t_crit / 3600, color='black', linestyle='-.', alpha=0.5)

ax1.set_xlabel('Čas [h]')
ax1.set_ylabel('Koncentrace O2 [mmol/L]', color='g')
ax1.tick_params(axis='y', labelcolor='g')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
R_t = np.array([get_R(ti) for ti in t_results])
ax2.plot(t_results / 3600, R_t * 1000, 'b-', alpha=0.3, label='R(t) - spotřeba')
ax2.set_ylabel('Respirační rychlost [mmol/L/s]', color='b')
ax2.tick_params(axis='y', labelcolor='b')

plt.title('Simulace kyslíkového režimu ve fermentoru (Solver)')
plt.tight_layout()
plt.savefig("fermentor_solver_plot.png", dpi=150)
print("Graf uložen do fermentor_solver_plot.png")


# Bioreactor Fermentor Simulation & Chemical Engineering Solvers

Numerical modeling of oxygen mass transfer in an aerated stirred-tank bioreactor alongside a curated collection of Maple chemical engineering unit-operation solvers.

## 1. Aerated Fermentor Dissolved-Oxygen ODE Solver (`fermentor_solver.py`)

Simulates a 15-hour aerobic batch fermentation (`V = 1200 L`, `T = 35 °C`, `Q_air = 3 L/s`) by numerically integrating the dissolved oxygen mass balance using `scipy.integrate.solve_ivp`:

```text
dc_L/dt = k_L·a · (c*(t) - c_L(t)) - R(t)
```

Key physical features modeled:
- **Gassed power input & volumetric mass-transfer coefficient (`k_L·a`)**: Computed from impeller power number (`Po`), broth density (`ρ`), agitation speed (`n`), impeller diameter (`d`), gassed power drop factor, and superficial gas velocity (`v_s`).
- **Dynamic off-gas depletion (`c*(t)`)**: Tracks residual oxygen in the exit gas stream as exponential biomass growth (`x(t) = x₀ · exp(μ·t)`) increases total oxygen uptake rate `R(t)`, using Henry's law constant for O₂ in water at 35 °C (`H = 1.07 × 10⁻⁸ mol/(L·Pa)`, Sander 2015).
- **Critical dissolved oxygen threshold (`c_crit`)**: Identifies the onset of oxygen limitation (`0.20 · c*(0)`) for bioreactor scale-up and aeration design.

### Run the Simulation

```bash
python fermentor_solver.py
```

Also included: `fermentor3.mw` (companion Maple symbolic/numerical worksheet).

## 2. Chemical Engineering II Maple Solvers (`maple_cheming2/`)

21 Maple (`.mpl`) analytical and numerical problem scripts covering core chemical engineering topics (see `maple_cheming2/00_obsah.md` for full index):
- **Topic 1 — Material & Energy Balances**: Rectification column, coal combustion
- **Topic 2 — Stirred Reactors**: Adiabatic batch & continuous CSTRs, cooled styrene CSTR
- **Topic 3 — Cascades & Tubular Reactors**: Plug-flow reactors (constant & variable flow), CSTR cascades
- **Topic 4 — Particle Size Distributions**: Number/volume conversions, log-normal catalyst attrition
- **Topic 5 — Sedimentation & Centrifuges**: Settler sizing, particle terminal velocity, centrifuge separation
- **Topic 6 — Fluidization**: Packed/fluidized bed pressure drop and minimum fluidization velocity
- **Topic 7 — Extraction**: Liquid-liquid extraction stage calculations

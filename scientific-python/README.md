# Scientific & Engineering Python Utilities

Standalone scientific computing, machine learning, signal analysis, and analytical chemistry scripts developed during coursework and independent research.

## Scripts

### 1. `gloti_climate_forecast.py` — NASA GLOTI Global Temperature Anomaly ML Forecaster
End-to-end time-series machine learning pipeline that ingests:
- **NASA GISTEMP v4** global land-ocean temperature index (GLOTI)
- **Copernicus ERA5** monthly/daily reanalysis proxies (via `cdsapi`)
- **NOAA** ENSO Niño 3.4, Mauna Loa CO₂, and stratospheric aerosol optical depth (SAOD) indices

Performs rolling `TimeSeriesSplit` cross-validation across `LinearRegression`, `ElasticNet`, `RandomForestRegressor`, `GradientBoostingRegressor`, and `MLPRegressor` pipelines to forecast monthly global temperature anomalies.

> **API Configuration:** Requires a Copernicus Climate Data Store key provided via environment variable (no credentials are stored in code):
> ```bash
> export CDSAPI_KEY="your-copernicus-cds-key"
> python gloti_climate_forecast.py --help
> ```

### 2. `s_plane_exponential.py` — Interactive s-Plane Visualizer
Interactive Matplotlib explorer for Laplace-domain poles `s = σ + jω` and their corresponding time-domain damped/growing sinusoids `Re{e^(st)} = e^(σt) cos(ωt)`. Click anywhere on the complex s-plane to update the real-time response; use arrow keys to adjust `t_max` and sampling resolution.

### 3. `ode_projectile_solver.py` — SciPy Numerical ODE Comparison
Compares numerical integration methods in `scipy.integrate.solve_ivp` for 2D ballistic/kinematic trajectories.

### 4. `analytical_chemistry_ascorbic_acid.py` — Analytical Chemistry Stoichiometry Helper
Serial-dilution and mass-fraction calculation helper for volumetric/analytical determination of ascorbic acid.

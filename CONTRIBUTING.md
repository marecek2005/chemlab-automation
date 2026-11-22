# Contributing to ChemLab Automation

Contributions, bug reports, hardware compatibility notes, and pull requests are welcome!

## Areas Where Contributions Help Most

- **Hardware Drivers & Instrumentation (`keithley-dmm6500/`)**: Additional TSP trigger models, SCPI compatibility, current/resistance modes, and cross-platform PyVISA backend fixes (Linux, macOS, Windows).
- **Optical Beam Profiling (`laser-beam-profiler/`)**: ISO 11146 second-moment (`D4σ`) calculation pipelines, automated Thorlabs CS165MU/M SDK capture scripts, and M² hyperbolic caustic fitting.
- **Process & Reactor Simulation (`fermentor-cheming/`)**: Additional chemical engineering unit operation models (CSTR, PFR, gas-liquid mass transfer, non-isothermal energy balances) ported to Python/SciPy.
- **AI Lab Automation (`ai-lab-protocol-skill/`)**: Multi-language support, LaTeX/Typst export targets, and automated uncertainty propagation checks.

## Development Workflow

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Install dependencies in a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Verify Python syntax before committing:
   ```bash
   python3 -m compileall .
   ```
4. Never commit API keys, personal credentials, or raw proprietary lab datasets. Use environment variables (e.g., `CDSAPI_KEY`) for external APIs.
5. Open a pull request describing the scientific or engineering change and how it was tested.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

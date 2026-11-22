#!/bin/bash
# Setup script for projetk_vslab conda environment
# Run this from the project root: bash setup_env.sh

set -e

echo "=== Setting up 'vslab' conda environment ==="

# Create the conda environment from environment.yml
conda env create -f environment.yml

echo ""
echo "=== Done! ==="
echo "To activate: conda activate vslab"
echo "Then in VS Code: Cmd+Shift+P → 'Python: Select Interpreter' → choose 'vslab'"

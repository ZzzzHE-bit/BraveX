#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$WORKSPACE_DIR"
source ~/curobo-main/.venv/bin/activate
echo "Running all benchmarks..."
python benchmark/benchmark.py --all --steps 15 --range 0.1
python visualization/plot.py
echo "All done!"

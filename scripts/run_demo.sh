#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$WORKSPACE_DIR"
source ~/curobo-main/.venv/bin/activate
CONFIG="${1:-dynamic}"
STEPS="${2:-15}"
RANGE="${3:-0.1}"
echo "Running demo with config: $CONFIG"
python benchmark/benchmark.py --config "$CONFIG" --steps "$STEPS" --range "$RANGE"
python visualization/plot.py
echo "Done! Check results/figures/"

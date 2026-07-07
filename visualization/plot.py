#!/usr/bin/env python3
# visualization/plot.py
import argparse
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def load_all_results(results_dir: Path) -> dict:
    data = {}
    for csv_path in results_dir.glob("*.csv"):
        config = csv_path.stem
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                data[config] = rows
    return data

def plot_comparison(data: dict, output_dir: Path):
    configs = list(data.keys())
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    
    # 1. Success Rate
    success_rates = []
    for c in configs:
        rows = data[c]
        sr = sum(1 for r in rows if r.get('success') == 'True') / len(rows) * 100
        success_rates.append(sr)
    axes[0,0].bar(configs, success_rates, color=colors[:len(configs)])
    axes[0,0].set_ylabel('Success Rate (%)')
    axes[0,0].set_title('Success Rate')
    axes[0,0].set_ylim(0,105)
    for i,v in enumerate(success_rates):
        axes[0,0].text(i, v+1, f'{v:.1f}%', ha='center')
    
    # 2. Planning Time
    times = []
    for c in configs:
        rows = data[c]
        vals = [float(r['plan_time']) for r in rows if r.get('success') == 'True']
        times.append(np.mean(vals) if vals else 0)
    axes[0,1].bar(configs, times, color=colors[:len(configs)])
    axes[0,1].set_ylabel('Avg Planning Time (s)')
    axes[0,1].set_title('Planning Time')
    
    # 3. Waypoints
    wps = []
    for c in configs:
        rows = data[c]
        vals = [float(r['total_wp']) for r in rows if r.get('success') == 'True']
        wps.append(np.mean(vals) if vals else 0)
    axes[1,0].bar(configs, wps, color=colors[:len(configs)])
    axes[1,0].set_ylabel('Avg Trajectory Waypoints')
    axes[1,0].set_title('Trajectory Length')
    
    # 4. Efficiency Score (成功率 / 时间)
    scores = []
    for i, c in enumerate(configs):
        if times[i] > 0:
            scores.append(success_rates[i] / times[i])
        else:
            scores.append(0)
    axes[1,1].bar(configs, scores, color=colors[:len(configs)])
    axes[1,1].set_ylabel('Efficiency Score')
    axes[1,1].set_title('Performance Score (SR / Time)')
    
    plt.tight_layout()
    out_path = output_dir / "comparison.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"📈 Figure saved to: {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default=None)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()
    workspace = Path(__file__).parent.parent
    input_dir = Path(args.input) if args.input else workspace / "results" / "csv"
    output_dir = Path(args.output) if args.output else workspace / "results" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    data = load_all_results(input_dir)
    if data:
        plot_comparison(data, output_dir)
    else:
        print("No data found. Run benchmark first.")

if __name__ == "__main__":
    main()

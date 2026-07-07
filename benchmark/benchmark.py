#!/usr/bin/env python3
# benchmark/benchmark.py
import argparse
import csv
import json
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from planner.dynamic_planner import DynamicPlanner

class BenchmarkRunner:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.results_dir = workspace_dir / "results" / "csv"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_single(self, config_name: str, steps: int = 15, move_range: float = 0.1) -> dict:
        # 先复制配置文件
        src_config = self.workspace_dir / "configs" / f"{config_name}.yaml"
        target_config = self.workspace_dir.parent / "curobo" / "content" / "configs" / "task" / "metrics_base.yml"
        if src_config.exists():
            shutil.copy(src_config, target_config)
            print(f"✅ Copied config '{config_name}' to cuRobo")
        else:
            print(f"⚠️ Config not found: {src_config}")
        
        # 调用原始脚本
        legacy_script = self.workspace_dir.parent / "my_projects" / "frankapick_moving_obstacle_v2.py"
        import subprocess
        import sys
        cmd = [
            sys.executable,
            str(legacy_script),
            "--moving",
            "--steps", str(steps),
            "--range", str(move_range),
            "--max-attempts", "3"
        ]
        print(f"🚀 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=str(legacy_script.parent.parent))
        
        # 读取结果
        import csv
        csv_path = Path.home() / ".cache" / "curobo" / "examples" / "motion_planning" / "moving_obstacle_metrics.csv"
        if csv_path.exists():
            # 复制到结果目录
            dest_csv = self.results_dir / f"{config_name}.csv"
            shutil.copy(csv_path, dest_csv)
            print(f"✅ Results saved to: {dest_csv}")
            
            # 计算摘要
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            success_count = sum(1 for r in rows if r.get('success') == 'True')
            total = len(rows)
            plan_times = [float(r['plan_time']) for r in rows if r.get('success') == 'True']
            avg_plan_time = sum(plan_times) / len(plan_times) if plan_times else 0
            waypoints = [float(r['total_wp']) for r in rows if r.get('success') == 'True']
            avg_waypoints = sum(waypoints) / len(waypoints) if waypoints else 0
            return {
                "config": config_name,
                "success_rate": success_count / total,
                "avg_plan_time": avg_plan_time,
                "avg_waypoints": avg_waypoints,
                "total_steps": total,
            }
        else:
            print(f"⚠️ Results CSV not found")
            return {"config": config_name, "success_rate": 0, "avg_plan_time": 0, "avg_waypoints": 0, "total_steps": 0}

    def run_all(self, configs: list = None, steps: int = 15, move_range: float = 0.1) -> dict:
        if configs is None:
            configs = ["official", "dynamic", "smooth", "safe"]
        all_summaries = {}
        for config in configs:
            print(f"\n{'='*50}\nRunning: {config}\n{'='*50}")
            summary = self.run_single(config, steps, move_range)
            all_summaries[config] = summary
            print(f"Summary: Success={summary['success_rate']*100:.1f}%, Time={summary['avg_plan_time']:.4f}s")
        summary_path = self.results_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(all_summaries, f, indent=2)
        print(f"\n📊 Summary saved to: {summary_path}")
        return all_summaries

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--steps", type=int, default=15)
    parser.add_argument("--range", type=float, default=0.1)
    args = parser.parse_args()
    workspace = Path(__file__).parent.parent
    runner = BenchmarkRunner(workspace)
    if args.all:
        runner.run_all(steps=args.steps, move_range=args.range)
    elif args.config:
        runner.run_single(args.config, args.steps, args.range)
    else:
        runner.run_single("dynamic", args.steps, args.range)

if __name__ == "__main__":
    main()

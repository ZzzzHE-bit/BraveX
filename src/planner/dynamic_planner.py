#!/usr/bin/env python3
# src/planner/dynamic_planner.py
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

class DynamicPlanner:
    def __init__(self, config_name: str, workspace_dir: Optional[Path] = None):
        self.config_name = config_name
        self.workspace_dir = workspace_dir or Path(__file__).parent.parent.parent
        self.results = []
        self._legacy_script = self.workspace_dir.parent / "my_projects" / "frankapick_moving_obstacle_v2.py"
        
        # 把配置文件复制到 cuRobo 目录
        self._apply_config(config_name)
    
    def _apply_config(self, config_name: str):
        """复制配置文件到 cuRobo"""
        src = self.workspace_dir / "configs" / f"{config_name}.yaml"
        target = self.workspace_dir.parent / "curobo" / "content" / "configs" / "task" / "metrics_base.yml"
        if src.exists() and target.exists():
            import shutil
            shutil.copy(src, target)
            print(f"✅ Copied config '{config_name}' to cuRobo")
        else:
            print(f"⚠️ Could not copy config: src={src.exists()}, target={target.exists()}")
    
    def run_experiment(self) -> List[Dict[str, Any]]:
        """通过子进程调用原始成功脚本"""
        if not self._legacy_script.exists():
            print(f"❌ Legacy script not found: {self._legacy_script}")
            return []
        
        # 构建命令，完全等同于用户成功运行时的命令
        cmd = [
            sys.executable,
            str(self._legacy_script),
            "--moving",
            "--steps", "15",
            "--range", "0.1",
            "--max-attempts", "3"
        ]
        
        print(f"🚀 Running legacy script: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=str(self._legacy_script.parent.parent))
        
        if result.returncode == 0:
            print("✅ Legacy script completed successfully")
        else:
            print(f"❌ Legacy script failed with code {result.returncode}")
        
        # 尝试读取生成的 CSV 作为结果
        import csv
        csv_path = Path.home() / ".cache" / "curobo" / "examples" / "motion_planning" / "moving_obstacle_metrics.csv"
        if csv_path.exists():
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                self.results = list(reader)
            print(f"📊 Loaded {len(self.results)} results from {csv_path}")
        else:
            print(f"⚠️ Results CSV not found at {csv_path}")
        
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.results:
            return {}
        success_count = sum(1 for r in self.results if r.get('success') == 'True')
        total = len(self.results)
        plan_times = [float(r['plan_time']) for r in self.results if r.get('success') == 'True']
        avg_plan_time = sum(plan_times) / len(plan_times) if plan_times else 0
        waypoints = [float(r['total_wp']) for r in self.results if r.get('success') == 'True']
        avg_waypoints = sum(waypoints) / len(waypoints) if waypoints else 0
        return {
            "config": self.config_name,
            "success_rate": success_count / total,
            "avg_plan_time": avg_plan_time,
            "avg_waypoints": avg_waypoints,
            "total_steps": total,
        }

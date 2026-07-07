#!/usr/bin/env python3
# src/planner/config_loader.py
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            self.config_dir = Path(__file__).parent.parent.parent / "configs"
        else:
            self.config_dir = Path(config_dir)

    def load(self, config_name: str) -> Dict[str, Any]:
        config_path = self.config_dir / f"{config_name}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def get_cost_weights(self, config_name: str) -> Dict[str, float]:
        return self.load(config_name).get("cost", {})

    def get_planner_params(self, config_name: str) -> Dict[str, Any]:
        return self.load(config_name).get("planner", {})

    def get_experiment_params(self, config_name: str) -> Dict[str, Any]:
        return self.load(config_name).get("experiment", {})

    def apply_to_curobo(self, config_name: str) -> None:
        """直接复制配置文件到 cuRobo，不重新生成"""
        src_path = self.config_dir / f"{config_name}.yaml"
        target_path = Path(__file__).parent.parent.parent.parent / "curobo" / "content" / "configs" / "task" / "metrics_base.yml"
        
        if not src_path.exists():
            print(f"⚠️ Source config not found: {src_path}")
            return
        
        if target_path.exists():
            shutil.copy(src_path, target_path)
            print(f"✅ Copied '{config_name}' directly to {target_path}")
        else:
            print(f"⚠️ Target path not found: {target_path}")

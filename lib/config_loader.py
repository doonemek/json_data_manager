# lib/config_loader.py の例
import json
from pathlib import Path

def load_config(config_path: str = "config/settings.json"):
    # プロジェクトルートからのパスとして確実に解決する書き方
    base_path = Path(__file__).parent.parent
    full_path = base_path / config_path
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)
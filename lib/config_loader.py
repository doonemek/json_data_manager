# lib/config_loader.py の例
import json
from pathlib import Path

def load_config(config_path: str = "config/settings.json"):
    """Config内容を読み出す

    Args:
        config_path (str, optional): 設定ファイルパス. Defaults to "config/settings.json".

    Returns:
        list: 設定リスト
    """
    base_path = Path(__file__).parent.parent
    full_path = base_path / config_path
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)
from pathlib import Path

from lib.json_hundler import load_json

def load_config(config_path: str = "config/settings.json") -> list:
    """Config内容を読み出す

    Args:
        config_path (str, optional): 設定ファイルパス. Defaults to "config/settings.json".

    Returns:
        list: 設定リスト
    """
    base_path = Path(__file__).parent.parent
    full_path = base_path / config_path
    
    return load_json(full_path)
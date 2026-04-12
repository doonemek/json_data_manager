from pathlib import Path

from lib.json_hundler import load_json

class ConfigLoader:
    def __init__(self, config_path="config/settings.json"):
        base_path = Path(__file__).parent.parent
        full_path = base_path / config_path

        self._config = load_json(full_path)
        self.common = self._config.get("common", {})


    Args:
        config_path (str, optional): 設定ファイルパス. Defaults to "config/settings.json".

    Returns:
        list: 設定リスト
    """
    base_path = Path(__file__).parent.parent
    full_path = base_path / config_path
    
    return load_json(full_path)
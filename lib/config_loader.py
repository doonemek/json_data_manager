import re
from pathlib import Path

from lib.json_hundler import load_json

class ConfigLoader:
    def __init__(self, config_path="config/settings.json"):
        base_path = Path(__file__).parent.parent
        full_path = base_path / config_path

        self._config = load_json(full_path)
        self.common = self._config.get("common", {})

    def _resolve_common_section(self, section: dict) -> dict:
        """共通設定とセクション設定をマージし、プレースホルダーを置換する

        Args:
            section (dict): 処理毎のセクション設定

        Returns:
            dict: 共通セクションを追加した処理毎のセクション設定
        """
        resolved = self.common.copy()
        resolved.update(section)
        
        # プレースホルダーの置換処理（resolved 全体を対象にする）
        for key, value in resolved.items():
            if isinstance(value, str):
                matches = re.findall(r"\$\{common\.([a-zA-Z0-9_]+)\}", value)
                for match in matches:
                    if match in self.common:
                        resolved[key] = value.replace(f"${{common.{match}}}", self.common[match])
        return resolved

    def get_deduplicator(self) -> dict:
        return self._resolve_common_section(self._config.get("deduplicator", {}))

    def get_sync_master_data(self) -> dict:
        return self._resolve_common_section(self._config.get("sync_master_data", {}))

    def get_splitter(self) -> dict:
        return self._resolve_common_section(self._config.get("splitter", {}))
    
    def get_inspector(self) -> dict:
        return self._resolve_common_section(self._config.get("inspector", {}))

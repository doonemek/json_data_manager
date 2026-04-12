import json
import logging
from pathlib import Path
from typing import Any

def load_json(file_path: Path) -> Any:
    """JSON読み込み

    汎用性を持たせるため、コード依存しないよう注意

    Args:
        file_path (Path): JSONファイルパス

    Returns:
        Any : JSON値
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
            logging.error(f"JSON形式不正: {file_path.name}")
    except Exception as e:
        logging.error(f"JSON読み込みエラー ({file_path}): {e}")
        return None

def save_json(data: Any, file_path: Path) -> None:
    """JSOファイル保存

    汎用性を持たせるため、コード依存しないよう注意

    Args:
        data (Any): JSON形式データ
        file_path (Path): 保存先ファイルパス
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"保存完了: {file_path}")
    except Exception as e:
        logging.error(f"保存エラー: {e}")
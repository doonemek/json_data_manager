import logging
from pathlib import Path

from lib.json_hundler import load_json

def analyze_counts(deduplicated_data: list[dict], analysis_keys: list[str]) -> dict:
    """抽出されたリストから各キーのユニークな件数をカウントする

    Args:
        deduplicated_data (list): 重複排除したデータリスト
        analysis_keys (list): カウント対象キー名リスト

    Returns:
        dict: 各キーとカウント値
    """
    counts = {}
    for k in analysis_keys:
        unique_values = {item.get(k) for item in deduplicated_data if item.get(k) is not None}
        counts[k] = len(unique_values)
    return counts

def deduplicate(target_list: list[dict], dedup_key: str, existing_keys: set | None = None) -> list[dict]:
    """既知のキー集合(existing_keys)に含まれないデータのみを抽出し、同時に既存の集合を更新する。

    existing_keys が存在しない場合は処理内で空setを準備する

    Args:
        target_list (list): 重複確認対象データリスト
        dedup_key (str): 重複制御キー
        existing_keys (set | None, optional): 既知のキー集合. Defaults to None.

    Returns:
        list: 重複を排除した新規データリスト
    """
    if existing_keys is None:
        existing_keys = set()

    unique_data = []
    for item in target_list:
        val = item.get(dedup_key)
        if val not in existing_keys:
            unique_data.append(item)
            existing_keys.add(val) # 呼び出し側のsetも更新される

    logging.debug(f"重複排除完了 (全件: {len(target_list)} 新規: {len(unique_data)} 重複: {len(target_list) - len(unique_data)})")
    return unique_data

def deduplicator(input_path: Path, dedup_key: str) -> list:
    """新規データリストから重複を排除したデータリストを作成する

    Args:
        input_path (Path): 新規データ格納パス
        dedup_key (str): 重複制御キー

    Returns:
        list: 重複排除新規データリスト
    """

    # 新規データの読み込み
    new_data_list = []
    json_files = list(Path(input_path).glob("*.json"))
    logging.info(f"新規データ収集開始: {len(json_files)} 件のファイルをスキャンします")

    for file_path in json_files:
        logging.debug(f"読み取り開始: {file_path.name}")
        try:
            # JSON ファイルを読み込み、リスト形式でなければ Skip する
            json_new_data = load_json(file_path)
            if not isinstance(json_new_data, list):
                logging.debug(f"リスト形式ではありません: {file_path.name}")
                continue

        except Exception as e:
            logging.error(f"読み込みエラー ({file_path.name}): {e}")

        new_data_list.extend(json_new_data)

    logging.info(f"新規データ収集完了: {len(new_data_list)} 件のデータを抽出しました")

    # 重複削除処理
    deduplicated_data_list = deduplicate(new_data_list, dedup_key)

    return deduplicated_data_list

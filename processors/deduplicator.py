import logging
import re
from pathlib import Path

from lib.json_hundler import load_json, save_json

def collect_unique_data(dedup_key: str, input_path: str) -> list:
    """指定ディレクトリ内の全JSONを読み込み、指定キーで重複排除したリストを返す

    Args:
        dedup_key (str): _description
        input_path (str): _description_

    Returns:
        list: 重複排除したリスト
    """
    deduplicated_data = []
    seen_keys = set()
    
    json_files = list(Path(input_path).glob("*.json"))
    logging.info(f"データ収集開始: {len(json_files)} 件のファイルをスキャンします")

    for file_path in json_files:
        logging.debug(f"読み取り開始: {file_path.name}")
        try:
            # JSON ファイルを読み込み、リスト形式でなければ Skip する
            data = load_json(file_path)
            if not isinstance(data, list):
                logging.debug(f"リスト形式ではありません: {file_path.name}")
                continue

            for item in data:
                key_value = item.get(dedup_key)
                if key_value is not None and key_value not in seen_keys:
                    deduplicated_data.append(item)
                    seen_keys.add(key_value)
                    
        except Exception as e:
            logging.error(f"読み込みエラー ({file_path.name}): {e}")

    logging.info(f"データ収集完了: {len(deduplicated_data)} 件のユニークなアイテムを抽出しました")
    return deduplicated_data

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


def _natural_sort_key(s: str) -> list:
    """文字列内の数字を数値として扱うためのソートキーを生成する。

    文字列を数字部分と文字部分に分割し、数値部分はintとして扱うことで、
    '10' が '2' より後に来るような自然な順序でのソートを実現する。

    Args:
        s (str): ソート対象の文字列

    Returns:
        list: ソート比較用のリスト（数値と文字列が混在）
    """
    if s is None: return []
    if not isinstance(s, str): return [s]
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def load_and_sort_data(data_list: list, sort_keys: list[str]) -> list:
    """設定キーに基づいて自然順ソートを行う

    数値文字列も数値として扱われるため、ID等の比較に最適化されている

    Args:
        data_list (list): JSON形式のデータリスト
        sort_keys (list[str]): ソートの優先順位となるキーのリスト

    Returns:
        list: ソート済みのJSON形式リスト。
    """
    # ソート処理
    return sorted(
        data_list,
        key=lambda item: [
            int(v) if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()) 
            else _natural_sort_key(str(v or "")) 
            for v in (item.get(k) for k in sort_keys)
        ]
    )

def save_json_data(deduplicated_data: list, analysis_results: dict, config: dict) -> str:
    """集計結果に基づいてファイル名を生成し、JSONを保存する

    集計結果はファイル名に記載される

    Args:
        deduplicated_data (list): 重複排除したリスト
        analysis_results (dict): 各キーとカウント値
        config (dict): 以下のキーが必要です:
            - analysis_keys (list): ファイル名の構成順序に使用
            - output_file_prefix (str): ファイル名の末尾
            - output_json_file_dir (str): 保存先ディレクトリ

    Returns:
        str: 作成されたファイル名
    """
    analysis_keys = config.get("analysis_keys", [])
    prefix = config.get("output_file_prefix", "result-total.json")
    
    filename_parts = [f"{k}-{analysis_results[k]}" for k in analysis_keys]
    final_filename = "_".join(filename_parts) + "_" + prefix
    
    output_path = Path(config.get("output_json_file_dir", "./output"))
    output_path.mkdir(exist_ok=True)
    output_file = output_path / final_filename
    
    save_json(deduplicated_data, output_file)
        
    logging.debug(f"保存完了: {final_filename} に {len(deduplicated_data)} 件を保存しました")
    return final_filename
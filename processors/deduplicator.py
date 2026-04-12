import logging
from pathlib import Path

from lib.json_hundler import load_json, save_json

def collect_unique_data(dedup_key: str, input_path: str):
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
        try:
            # JSON ファイルを読み込み、リスト形式でなければ Skip する
            data = load_json(file_path)
            if not isinstance(data, list):
                logging.debug(f"リスト形式ではありません: {file_path}")
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

def analyze_counts(deduplicated_data: list, analysis_keys: list):
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

def save_json_data(deduplicated_data: list, analysis_results: dict, config: dict):
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
        
    logging.info(f"保存完了: {final_filename} に {len(deduplicated_data)} 件を保存しました")
    return final_filename
import json
import logging
from pathlib import Path

def get_deduplicated_list(config: any):
    """指定ディレクトリ内の全JSONを読み込み、指定キーで重複排除したリストを返す

    analysis_keys に設定したkey名とファイル内のユニークな数をファイル名に追記する

    Args:
        config (any): Config ファイルの設定値

    Returns:
        list: 重複を排除した統合リスト
    """
    dedup_key = config.get("dedup_key", "id")
    path = Path(config.get("input_json_file_dir", "./data"))
    
    deduplicated_list = []
    seen_keys = set()
    
    json_files = list(path.glob("*.json"))
    logging.info(f"データ収集開始: {len(json_files)} 件のファイルをスキャンします。")

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                continue

            for item in data:
                # 設定されたキーを取得
                key_value = item.get(dedup_key)
                
                # キーが存在し、かつ未登録の場合のみ追加
                if key_value is not None and key_value not in seen_keys:
                    deduplicated_list.append(item)
                    seen_keys.add(key_value)
                    
        except Exception as e:
            logging.error(f"読み込みエラー ({file_path.name}): {e}")
    
    # key カウント処理（ユニークな値の数を数える）
    analysis_keys = config.get("analysis_keys", [])
    
    # ファイル名用のパーツリスト
    filename_parts = []
    
    for k in analysis_keys:
        # deduplicated_list から対象キーの値をすべて抽出し、集合(set)にしてユニークな個数を取得
        unique_values = {item.get(k) for item in deduplicated_list if item.get(k) is not None}
        count = len(unique_values)
        
        # パーツとして追加
        filename_parts.append(f"{k}-{count}")
    
    # ファイル名生成
    prefix = config.get("output_file_prefix", "result-total.json")
    final_filename = "_".join(filename_parts) + "_" + prefix
    
    # 保存処理
    output_path = Path(config.get("output_json_file_dir", "./output"))
    output_path.mkdir(exist_ok=True)
    output_file = output_path / final_filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(deduplicated_list, f, ensure_ascii=False, indent=4)
        
    logging.info(f"保存完了: {final_filename} に {len(deduplicated_list)} 件を保存しました。")
    
    return deduplicated_list
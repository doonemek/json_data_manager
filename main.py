import logging
from pathlib import Path

from lib.config_loader import load_config
from lib.json_hundler import save_json
from lib.logger import setup_logger
from processors.deduplicator import load_master_data, collect_unique_data, filter_new_data, analyze_counts, load_and_sort_data, generate_filename
from processors.inspector import inspector

setup_logger()

def main():
    
    logging.info("Process Start")
    # config 読み込み
    config = load_config()

    # master データの読み込み
    master_data = load_master_data(config.get("master_json_file_dir", "./data/master"))

    # データ統合・重複除去
    deduplicated_data = collect_unique_data(config.get("dedup_key", "id"),config.get("input_json_file_dir", "./data"))

    # master データと 新規データを比較し、完全新規データを抽出
    new_unique_data = filter_new_data(deduplicated_data, master_data, config.get("dedup_key", "id"))

    # master データに新規データを結合
    master_data.extend(new_unique_data)

    # 統合データのソート
    sorted_unique_data = load_and_sort_data(new_unique_data, config.get("analysis_keys", ["id"]))
    sorted_master_data = load_and_sort_data(master_data, config.get("analysis_keys", ["id"]))

    # 特定キーカウントアップ
    keys = config.get("analysis_keys") or [config.get("dedup_key", "id")]
    analysis_result_new_unique_data = analyze_counts(new_unique_data, keys)
    analysis_result_master_data = analyze_counts(master_data, keys)

    # 対象データファイル名生成
    unique_data_filename = generate_filename(analysis_result_new_unique_data, config.get("analysis_keys"),config.get("output_unique_file_prefix"))
    master_data_filename = generate_filename(analysis_result_master_data, config.get("analysis_keys"),config.get("output_master_file_prefix"))

    # 新規データが存在する場合、各種データ保存
    if sorted_unique_data:
        output_dir = Path(config.get("output_json_file_dir"))
        unique_data_file_path = output_dir / unique_data_filename
        save_json(sorted_unique_data, unique_data_file_path)
        master_dir = Path(config.get("master_json_file_dir"))
        master_data_file_path = master_dir / master_data_filename
        save_json(sorted_master_data, master_data_file_path)

    # 解析
    inspector()

    ###　今後追加予定
    # データ保存

    logging.info("Process End")

if __name__ == "__main__":
    main()
from lib.config_loader import load_config
from lib.logger import setup_logger
from processors.inspector import inspect_json_files
from processors.deduplicator import collect_unique_data, analyze_counts, save_json_data
import logging

setup_logger()

def main():
    
    logging.info("Process Start")
    # config 読み込み
    config = load_config()

    # データ統合・重複除去
    deduplicated_data = collect_unique_data(config.get("dedup_key", "id"),config.get("input_json_file_dir", "./data"))

    keys = config.get("analysis_keys") or [config.get("dedup_key", "id")]
    analysis_results = analyze_counts(deduplicated_data, keys)
    save_json_data(deduplicated_data, analysis_results, config)

    # 統合データのソート
    # sorted_data = load_and_sort_data(file_path, sort_keys)

    # 解析
    # inspect_json_files("./data")

    ###　今後追加予定
    # データ保存

    logging.info("Process End")

if __name__ == "__main__":
    main()
from lib.config_loader import load_config
from lib.logger import setup_logger
from processors.inspector import inspector
from processors.deduplicator import collect_unique_data, analyze_counts, load_and_sort_data, save_json_data
import logging

setup_logger()

def main():
    
    logging.info("Process Start")
    # config 読み込み
    config = load_config()

    # データ統合・重複除去
    deduplicated_data = collect_unique_data(config.get("dedup_key", "id"),config.get("input_json_file_dir", "./data"))

    # 特定キーカウントアップ
    keys = config.get("analysis_keys") or [config.get("dedup_key", "id")]
    analysis_results = analyze_counts(deduplicated_data, keys)

    # 統合データのソート
    sorted_data = load_and_sort_data(deduplicated_data, config.get("sort_keys", ["id"]))

    # 対象データを保存
    save_json_data(sorted_data, analysis_results, config)

    # 解析
    inspector()

    ###　今後追加予定
    # データ保存

    logging.info("Process End")

if __name__ == "__main__":
    main()
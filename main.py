from lib.config_loader import load_config
from lib.logger import setup_logger
from processors.inspector import inspect_json_files
from processors.deduplicator import get_deduplicated_list
import logging

setup_logger()

def main():
    
    logging.info("Process Start")
    # config 読み込み
    config = load_config()

    # データ統合・重複除去
    all_data = get_deduplicated_list(config)

    # 統合データのソート
    # sorted_data = load_and_sort_data(file_path, sort_keys)

    # 解析
    # inspect_json_files("./data")

    ###　今後追加予定
    # データ保存

    logging.info("Process End")

if __name__ == "__main__":
    main()
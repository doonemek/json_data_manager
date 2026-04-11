from lib.logger import setup_logger
from processors.inspector import inspect_json_files
from processors.deduplicator import combine_and_deduplicate_json
import logging

setup_logger()

def main():
    
    logging.info("Process Start")

    # データ統合・重複除去
    combine_and_deduplicate_json("./data", "./output", id_key="id")

    # 統合データのソート

    # 解析
    inspect_json_files("./data")

    ###　今後追加予定
    # データ保存

    logging.info("Process End")

if __name__ == "__main__":
    main()
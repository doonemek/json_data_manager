import logging
from pathlib import Path

from lib.config_loader import ConfigLoader
from lib.json_hundler import save_json
from lib.logger import setup_logger
from processors.deduplicator import deduplicator
from processors.inspector import inspector
from processors.sync_master_data import sync_master_data
from processors.splitter import splitter, split_by_group
from utils.data_tools import load_and_sort_data

setup_logger()

def main():
    
    logging.info("Process Start")
    # config 読み込み
    config_loader = ConfigLoader()
    dedup_conf = config_loader.get_deduplicator()
    sync_master_data_conf = config_loader.get_sync_master_data()
    splitter_conf = config_loader.get_splitter()

    # 重複排除処理呼び出し
    deduplicated_data = deduplicator(dedup_conf["input_json_file_dir"], dedup_conf["dedup_key"])

    # 新規データをソート処理
    sorted_deduplicated_data = load_and_sort_data(deduplicated_data, dedup_conf["analysis_keys"])

    # 新規データのグループ化
    grouped_new_data = split_by_group(sorted_deduplicated_data, sync_master_data_conf["group_key"], sync_master_data_conf["group_range"])

    # master 操作関数呼び出し(sync_master_data)
    new_unique_data = sync_master_data(grouped_new_data, sync_master_data_conf)

    # 完全新規データが存在する場合に処理実施
    if new_unique_data:

        # 統合データのソート
        sorted_unique_data = load_and_sort_data(new_unique_data, dedup_conf["analysis_keys"])

        # データを特定数毎に分割
        split_lists = splitter(sorted_unique_data, splitter_conf["split_key"], splitter_conf["split_num"])

        # データ分割保存
        total_splits = len(split_lists)
        for i, split_data in enumerate(split_lists, 1):

            # 番目を 0 埋め
            paddend_i = f"{i:0{len(str(total_splits))}d}"

            # config から prefix 整形
            prefix = splitter_conf["output_json_file_pefix"].format(file_counts=paddend_i)

            # ファイル保存
            unique_data_filename = generate_filename(split_data, splitter_conf["split_key"], prefix)
            save_json(split_data, Path(dedup_conf["output_json_file_dir"]) / unique_data_filename)

        # 古い master をアーカイブ or 削除処理

    # 解析
    inspector()

    # # 特定キーカウントアップ
    # keys = _conf["analysis_keys"]
    # analysis_result_new_unique_data = analyze_counts(new_unique_data, keys)
    # analysis_result_master_data = analyze_counts(master_data, keys)

    logging.info("Process End")

if __name__ == "__main__":
    main()
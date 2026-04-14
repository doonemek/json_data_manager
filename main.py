import logging
from pathlib import Path

from lib.config_loader import ConfigLoader
from lib.json_hundler import save_json
from lib.logger import setup_logger
from processors.deduplicator import load_master_data, convert_from_list_to_dict, collect_unique_data, filter_new_data, analyze_counts, load_and_sort_data, generate_filename
from processors.inspector import inspector
from processors.splitter import splitter

setup_logger()

def main():
    
    logging.info("Process Start")
    # config 読み込み
    config_loader = ConfigLoader()
    dedup_conf = config_loader.get_deduplicator()
    splitter_conf = config_loader.get_splitter()

    # master データの読み込み
    master_data = load_master_data(dedup_conf["master_json_file_dir"])

    # master データ dict変換 (検索を高速化するため)
    master_dict = convert_from_list_to_dict(master_data, dedup_conf["dedup_key"])

    # データ統合・重複除去
    deduplicated_data = collect_unique_data(dedup_conf["dedup_key"],dedup_conf["input_json_file_dir"])

    # master データと 新規データを比較し、
    new_unique_data = filter_new_data(deduplicated_data, master_dict, dedup_conf["dedup_key"])

    # 完全新規データが存在する場合に処理実施
    if new_unique_data:
        # master データに新規データを結合
        master_data.extend(new_unique_data)

        # 統合データのソート
        sorted_unique_data = load_and_sort_data(new_unique_data, dedup_conf["analysis_keys"])
        sorted_master_data = load_and_sort_data(master_data, dedup_conf["analysis_keys"])

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

        master_data_filename = generate_filename(sorted_master_data, dedup_conf["pickup_key"],dedup_conf["output_master_file_prefix"])

        # 各種データ保存
        save_json(sorted_unique_data, Path(dedup_conf["output_json_file_dir"]) / unique_data_filename)
        save_json(sorted_master_data, Path(dedup_conf["master_json_file_dir"]) / master_data_filename)

    # 解析
    inspector()

    # # 特定キーカウントアップ
    # keys = _conf["analysis_keys"]
    # analysis_result_new_unique_data = analyze_counts(new_unique_data, keys)
    # analysis_result_master_data = analyze_counts(master_data, keys)

    logging.info("Process End")

if __name__ == "__main__":
    main()
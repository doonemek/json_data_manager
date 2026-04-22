import logging
from pathlib import Path

from lib.json_hundler import load_json, save_json
from processors.splitter import get_range_from_value
from processors.deduplicator import deduplicate
from utils.data_tools import load_and_sort_data

def sync_master_data(grouped_new_data: list[list[dict]], sync_master_data_conf: dict) -> list[dict]:
    """master データと新規データの比較をし、新規データを追加した master データを保存する

    比較する際にはグループ化された範囲で比較し、高速化する
    新規データがない場合はmasetr データの操作は行わない

    Args:
        grouped_new_data (list[list[dict]]): グループ化された検証データリスト
        sync_master_data_conf (dict): sync_master_data で使用する設定値

    Returns:
        list[dict]: 完全新規データリスト
    """
    logging.info(f"{len(grouped_new_data)} 件のグループに対して master データ比較処理開始")

    unique_new_data = []
    data_counts = 0
    for group in grouped_new_data:
        data_counts += len(group)
        # master データファイルの範囲をグループから検出
        min_val, max_val = get_range_from_value(group[0][sync_master_data_conf["group_key"]], sync_master_data_conf["group_range"])

        # master データファイルのファイル名を生成
        target_master_filename = sync_master_data_conf["output_master_file_prefix"].format(group_key=sync_master_data_conf["group_key"], min_val=min_val, max_val=max_val) + ".json"
        target_master_file_path = Path(sync_master_data_conf["master_json_file_dir"]) / target_master_filename

        if target_master_file_path.exists():
            # 既存 master 更新処理
            logging.debug(f"{min_val}-{max_val} の master データに対して重複排除実施")
            master_data = load_json(target_master_file_path)

            # master データと新規データを比較 (完全新規データを抽出)
            master_keys = {item[sync_master_data_conf["dedup_key"]] for item in master_data}
            unique_new = deduplicate(group, sync_master_data_conf["dedup_key"], master_keys)

            if not unique_new:
                # 新規データがないため、masterデータ更新しない
                continue

            # master + 新規データ 統合
            new_master_data = master_data + unique_new

            # 正確に保存するためソートを実施
            new_master_data = load_and_sort_data(new_master_data, sync_master_data_conf["analysis_keys"])

        else:
            # 完全新規グループのため全件 master データ化
            new_master_data = group
            unique_new = group

        if new_master_data:
            # master データ保存
            save_json(new_master_data, target_master_file_path)

            # 完全新規データ追加
            unique_new_data.extend(unique_new)

    # 完全新規データ群を main に返却
    logging.debug(f"{data_counts} 中 {len(unique_new_data)} 件が完全新規データ")
    return unique_new_data

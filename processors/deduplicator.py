import logging
import re
from pathlib import Path

from lib.json_hundler import load_json

def load_master_data(master_dir: str = "./data/master") -> list[dict]:
    """./data/master 内の全JSONファイルを読み込み、リスト化して返す

    Args:
        master_dir (str, optional): master データ保存場所. Defaults to "./data/master".

    Returns:
        list[dict]: master データのリスト (存在しない場合は空のリストを返す)
    """
    master_path = Path(master_dir)
    master_list = []

    if not master_path.exists():
        logging.info(f"data 配下に master が存在しないため、作成します: {master_dir}.")
        master_path.mkdir(exist_ok=True)
        return master_list

    # JSONファイルのみを対象にループ
    json_files = list(Path(master_path).glob("*.json"))
    logging.info(f"master データ収集開始: {len(json_files)} 件のファイルをスキャンします")
    for file_path in json_files:
        logging.debug(f"読み取り開始: {file_path.name}")

        data = load_json(file_path)
        if data is None:
            logging.warning(f"データがありません: {file_path}")
            continue
        
        # 読み込んだデータがリスト形式でないなら Skip
        if not isinstance(data, list):
            logging.debug(f"リスト形式ではありません: {file_path.name}")
            continue

        # master データ追加
        master_list.extend(data)
            
    logging.info(f"master データ読み込み完了: {len(master_list)} 件のアイテムを抽出しました")
    return master_list

def convert_from_list_to_dict(list_data: list[dict], index_key: str) -> dict:
    """辞書型のリストデータを、指定キーで辞書データに変換する

    [前提]
    index_key が重複している場合、より後に読み込まれたデータに上書きされる

    [データ構成]
    list[dict] → {<index_key>: <dict_item>]}

    Args:
        list_data (list[dict]): 辞書型のリストデータ
        index_key (str): 辞書型で使用するキー名

    Returns:
        dict: 変換された辞書データ
    """
    return {item[index_key]: item for item in list_data}

def collect_unique_data(dedup_key: str, input_path: str) -> list:
    """指定ディレクトリ内の全JSONを読み込み、指定キーで重複排除したリストを返す

    Args:
        dedup_key (str): 重複排除するためのキー
        input_path (str): 入力データパス

    Returns:
        list: 重複排除したリスト
    """
    deduplicated_data = []
    seen_keys = set()
    
    json_files = list(Path(input_path).glob("*.json"))
    logging.info(f"新規データ収集開始: {len(json_files)} 件のファイルをスキャンします")

    for file_path in json_files:
        logging.debug(f"読み取り開始: {file_path.name}")
        try:
            # JSON ファイルを読み込み、リスト形式でなければ Skip する
            data = load_json(file_path)
            if not isinstance(data, list):
                logging.debug(f"リスト形式ではありません: {file_path.name}")
                continue

            for item in data:
                key_value = item.get(dedup_key)
                if key_value is not None and key_value not in seen_keys:
                    deduplicated_data.append(item)
                    seen_keys.add(key_value)
                    
        except Exception as e:
            logging.error(f"読み込みエラー ({file_path.name}): {e}")

    logging.info(f"新規データ収集完了: {len(deduplicated_data)} 件のユニークなアイテムを抽出しました")
    return deduplicated_data

def filter_new_data(new_data: list[dict], master_dict: dict, dedup_key: str) -> list[dict]:
    """master データに含まれない新規データを抽出する
    判定は dedup_keys で登録された key で行う

    Args:
        new_data (list[dict]): 新規データから重複排除したリスト
        master_dict (dict): master データ
        dedup_key (str): 重複排除の条件キー

    Returns:
        list[dict]: master データに存在しない新規データリスト
    """
    unique_to_master = []
    
    for item in new_data:
        # 重複チェック（O(1)の爆速検索）
        if item[dedup_key] not in master_dict:
            unique_to_master.append(item)
    
    logging.info(f"重複排除完了: {len(new_data)} 件中 {len(unique_to_master)} 件が新規データです")
    return unique_to_master

def analyze_counts(deduplicated_data: list[dict], analysis_keys: list[str]) -> dict:
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


def _natural_sort_key(s: str) -> list:
    """文字列内の数字を数値として扱うためのソートキーを生成する。

    文字列を数字部分と文字部分に分割し、数値部分はintとして扱うことで、
    '10' が '2' より後に来るような自然な順序でのソートを実現する。

    Args:
        s (str): ソート対象の文字列

    Returns:
        list: ソート比較用のリスト（数値と文字列が混在）
    """
    if s is None: return []
    if not isinstance(s, str): return [s]
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def load_and_sort_data(data_list: list, sort_keys: list[str]) -> list:
    """設定キーに基づいて自然順ソートを行う

    数値文字列も数値として扱われるため、ID等の比較に最適化されている

    Args:
        data_list (list): JSON形式のデータリスト
        sort_keys (list[str]): ソートの優先順位となるキーのリスト

    Returns:
        list: ソート済みのJSON形式リスト。
    """
    # ソート処理
    return sorted(
        data_list,
        key=lambda item: [
            int(v) if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()) 
            else _natural_sort_key(str(v or "")) 
            for v in (item.get(k) for k in sort_keys)
        ]
    )

def generate_filename(sorted_data_list: list[dict], pickup_key: str, prefix: str = "") -> str:
    """ソート済みデータリストの先頭・末尾からファイル名を生成する。
    
    prefixが指定されている場合は、ファイル名の先頭に付与する。

    Args:
        sorted_data_list (list[dict]): ソート済みデータリスト
        pickup_key (str): 指定対象キー
        prefix (str, optional): _description_. Defaults to "".

    Returns:
        str: _description_
    """
    min_id = sorted_data_list[0][pickup_key]
    max_id = sorted_data_list[-1][pickup_key]

    filename = f"{pickup_key}_{min_id}-{max_id}.json"
    
    # prefix がある場合は "{prefix}_" を付与し、ない場合はそのまま出力
    if prefix:
        return f"{prefix}_{filename}"
    else:
        return filename

def deduplicate(target_list: list[dict], dedup_key: str, existing_keys: set | None = None) -> list[dict]:
    """既知のキー集合(existing_keys)に含まれないデータのみを抽出し、同時に既存の集合を更新する。

    existing_keys が存在しない場合は処理内で空setを準備する

    Args:
        target_list (list): 重複確認対象データリスト
        dedup_key (str): 重複制御キー
        existing_keys (set | None, optional): 既知のキー集合. Defaults to None.

    Returns:
        list: 重複を排除した新規データリスト
    """
    if existing_keys is None:
        existing_keys = set()

    unique_data = []
    for item in target_list:
        val = item.get(dedup_key)
        if val not in existing_keys:
            unique_data.append(item)
            existing_keys.add(val) # 呼び出し側のsetも更新される

    logging.debug(f"重複排除完了 (全件: {len(target_list)} 新規: {len(unique_data)} 重複: {len(target_list) - len(unique_data)})")
    return unique_data

def deduplicator(input_path: Path, dedup_key: str) -> list:
    """新規データリストから重複を排除したデータリストを作成する

    Args:
        input_path (Path): 新規データ格納パス
        dedup_key (str): 重複制御キー

    Returns:
        list: 重複排除新規データリスト
    """

    # 新規データの読み込み
    new_data_list = []
    json_files = list(Path(input_path).glob("*.json"))
    logging.info(f"新規データ収集開始: {len(json_files)} 件のファイルをスキャンします")

    for file_path in json_files:
        logging.debug(f"読み取り開始: {file_path.name}")
        try:
            # JSON ファイルを読み込み、リスト形式でなければ Skip する
            json_new_data = load_json(file_path)
            if not isinstance(json_new_data, list):
                logging.debug(f"リスト形式ではありません: {file_path.name}")
                continue

        except Exception as e:
            logging.error(f"読み込みエラー ({file_path.name}): {e}")

        new_data_list.extend(json_new_data)

    logging.info(f"新規データ収集完了: {len(new_data_list)} 件のデータを抽出しました")

    # 重複削除処理
    deduplicated_data_list = deduplicate(new_data_list, dedup_key)

    return deduplicated_data_list

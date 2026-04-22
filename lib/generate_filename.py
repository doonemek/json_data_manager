
def generate_filename(sorted_data_list: list[dict], pickup_key: str, prefix: str = "") -> str:
    """ソート済みデータリストの先頭・末尾からファイル名を生成する。
    
    prefixが指定されている場合は、ファイル名の先頭に付与する。

    Args:
        sorted_data_list (list[dict]): ソート済みデータリスト
        pickup_key (str): 指定対象キー
        prefix (str, optional): ファイル名接頭辞. Defaults to "".

    Returns:
        str: ファイル名
    """
    min_id = sorted_data_list[0][pickup_key]
    max_id = sorted_data_list[-1][pickup_key]

    filename = f"{pickup_key}_{min_id}-{max_id}.json"
    
    # prefix がある場合は "{prefix}_" を付与し、ない場合はそのまま出力
    if prefix:
        return f"{prefix}_{filename}"
    else:
        return filename
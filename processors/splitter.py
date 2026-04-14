def splitter(data_list: list[dict], split_key: str, split_num: int) -> list[list[dict]]:
    """ソート済みデータリストを、split_key単位でグループ化し、
    それをsplit_num個ずつまとめて分割する

    Args:
        data_list (list[dict]): ソート済みデータリスト
        split_key (str): グループ分け指定キー
        split_num (int): 1ファイルの最低要素数

    Returns:
        list[list[dict]]: split_num で分割されたリスト群
    """
    if not data_list:
        return []

    # 同じキーを持つ要素をグループ化 (ソート済みなので隣接のみチェック)
    groups = []
    current_group = [data_list[0]]
    
    for item in data_list[1:]:
        if item[split_key] == current_group[-1][split_key]:
            current_group.append(item)
        else:
            groups.append(current_group)
            current_group = [item]
    groups.append(current_group)  # 最後のグループを追加

    # グループ単位で split_num 個ずつに分割
    return [
        [item for group in groups[i : i + split_num] for item in group]
        for i in range(0, len(groups), split_num)
    ]
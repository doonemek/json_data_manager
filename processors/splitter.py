from itertools import groupby

def get_range_from_value(target_value: int, group_range: int) -> tuple[int, int]:
    """渡された値の属する範囲の上下限を取得する

    Args:
        target_value (int): 範囲を特定したい値
        group_range (int): 範囲区切り数

    Returns:
        tuple[int, int]: 範囲の上下限値
    """
    min_val = ((target_value - 1) // group_range) * group_range + 1
    max_val = min_val + group_range - 1
    return min_val, max_val


def split_by_group(data_list, group_key, group_range):
    """data_list を group_key の値に基づいて範囲ごとにリスト化する。

    戻り値: [[{...}, {...}], [{...}, {...}], ...]

    Args:
        data_list (list[dict]): グループ分け対象データリスト
        group_key (string): グループ分けしたいキー名
        group_range (int): グループ区切り数
    """

    def get_group_key(data):
        # グループ分けのキーとなる計算式（再計算のベース）
        # (id-1) // range はその範囲の開始インデックスを特定する
        target_id = data[group_key]
        return (target_id - 1) // group_range

    # グループ化してリストのリストへ変換
    result = []
    for _, group in groupby(data_list, key=get_group_key):
        result.append(list(group))

    return result

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

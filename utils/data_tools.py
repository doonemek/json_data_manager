import re

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

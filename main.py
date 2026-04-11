import json
import pathlib

from lib.config_loader import load_config

def load_and_sort_data(file_path: pathlib.Path, sort_keys: list):
    """JSONファイルを読み込み、設定キーに基づいて自然順ソートを行う。

    辞書形式のリストを読み込み、指定されたソートキーに従って並び替える。
    数値文字列も数値として扱われるため、ID等の比較に最適化されている。

    Args:
        file_path (pathlib.Path): 読み込むJSONファイルのパス。
        sort_keys (list): ソートの優先順位となるキーのリスト。

    Returns:
        list: ソート済みの辞書リスト。

    Raises:
        ValueError: 読み込んだJSONデータがリスト形式でない場合に発生。
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if not isinstance(data, list):
        raise ValueError(f"リスト形式ではありません: {file_path}")

    # ソート処理
    return sorted(
        data,
        key=lambda item: [
            int(v) if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()) 
            else natural_sort_key(str(v or "")) 
            for v in (item.get(k) for k in sort_keys)
        ]
    )

def inspect_json_files(target_dir: str):
    """指定ディレクトリ内の全JSONファイルを読み込み、ソート結果を表示する。

    設定ファイルからターゲットキーを取得し、各ファイルのデータから
    指定された件数分のみをコンソールに出力する。

    Args:
        target_dir (str): JSONファイルが格納されているディレクトリのパス。
    """
    config = load_config()
    target_keys = config.get("target_keys", [])
    sort_keys = config.get("sort_keys", [])
    display_limit = config.get("display_limit", 5)

    path = pathlib.Path(target_dir)
    json_files = list(path.glob("*.json"))

    if not json_files:
        print(f"JSONファイルが見つかりません: {target_dir}")
        return

    for file_path in json_files:
        print(f"\n--- File: {file_path.name} ---")
        try:
            # ここでデータ処理を分離
            sorted_data = load_and_sort_data(file_path, sort_keys)
            
            # 表示処理
            for item in sorted_data[:display_limit]:
                print({k: item.get(k, "N/A") for k in target_keys})
            print(f"... (全 {len(sorted_data)} 件中)")
            
        except json.JSONDecodeError:
            print(f"JSONの形式が正しくありません: {file_path.name}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました ({file_path.name}): {e}")

if __name__ == "__main__":
    inspect_json_files("./data")
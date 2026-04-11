import json
import pathlib

from lib.config_loader import load_config

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
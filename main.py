import json
import pathlib

from lib.config_loader import load_config

def inspect_json_files(target_dir: str):
    path = pathlib.Path(target_dir)
    json_files = list(path.glob("*.json"))

    if not json_files:
        print(f"JSONファイルが {target_dir} に見当たりません。")
        return
    
    config = load_config()
    target_keys = config["target_keys"]
    deisplay_limit = config["display_limit"]

    for file_path in json_files:
        print(f"\n--- File: {file_path.name} ---")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if isinstance(data, list):
                    for item in data[:deisplay_limit]:
                        # 指定したキーだけを抽出して表示
                        extracted = {key: item.get(key, "N/A") for key in target_keys}
                        print(extracted)
                    print(f"... (全 {len(data)} 件中)")
                else:
                    print("データはリスト形式ではありません。")
        except Exception as e:
            print(f"読み込みエラー: {e}")

if __name__ == "__main__":
    inspect_json_files("./data")
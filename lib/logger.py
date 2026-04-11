import logging
import sys
from pathlib import Path

def setup_logger(log_dir: str = "logs"):
    """ログの設定：ファイルとコンソールへ同時に出力する

    DEGUB以上でログ・コンソール出力、INFO以上でコンソールのみ出力

    Args:
        log_dir (str, optional): ログファイルを吐き出すディレクトリ. Defaults to "logs".
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # ルートロガーの取得
    logger = logging.getLogger()

    # 【重要】既にハンドラがある場合は処理を中断する（ガード節）
    if logger.hasHandlers():
        return
    
    logger.setLevel(logging.DEBUG)  # すべてのログを対象にする

    # 共通フォーマット
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # ファイルハンドラ（詳細記録用：DEBUG以上）
    file_handler = logging.FileHandler(log_path / "app.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # コンソールハンドラ（画面表示用：INFO以上）
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
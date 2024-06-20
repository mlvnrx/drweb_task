import os
from db import add_user


def get_file_path(store_dir: str, file_hash: str) -> str:
    return os.path.join(store_dir, file_hash[:2], file_hash)


def init_db():
    try:
        add_user("admin", "password")
    except Exception as e:
        print(f"SQLite Error: {e}")

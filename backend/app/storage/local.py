import os
import uuid

from .base import StorageBackend


class LocalStorage(StorageBackend):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save(self, file_content: bytes, filename: str) -> str:
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        full_path = os.path.join(self.base_dir, unique_name)
        with open(full_path, "wb") as f:
            f.write(file_content)
        return unique_name

    def read(self, path: str) -> bytes:
        full_path = os.path.join(self.base_dir, path)
        with open(full_path, "rb") as f:
            return f.read()

    def delete(self, path: str) -> None:
        full_path = os.path.join(self.base_dir, path)
        if os.path.exists(full_path):
            os.remove(full_path)
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def save(self, file_content: bytes, filename: str) -> str:
        """Save file content, return a path/key that can later retrieve it."""

    @abstractmethod
    def read(self, path: str) -> bytes:
        """Retrieve file content given the path/key."""

    @abstractmethod
    def delete(self, path: str) -> None:
        """Remove the file."""
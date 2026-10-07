from app.core.exceptions import FileTooLargeError, InvalidFileTypeError

PDF_MAGIC_BYTES = b"%PDF-"
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def validate_resume_file(content: bytes) -> None:
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(max_mb=5)

    if content[:5] != PDF_MAGIC_BYTES:
        raise InvalidFileTypeError()
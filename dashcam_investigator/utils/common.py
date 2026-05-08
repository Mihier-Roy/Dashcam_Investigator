from hashlib import sha256
from pathlib import Path
from typing import Tuple


def generate_file_hash(file_path: Path) -> str:
    """
    This function reads an input file and computes the SHA256 hash of the file.
    param: file_path -> Path of the file to be hashed
    returns: hash -> Hexadecimal representation of the SHA256 hash.
    """
    hash_function = sha256()
    with file_path.open("rb") as file:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: file.read(4096), b""):
            hash_function.update(byte_block)
        return hash_function.hexdigest()


def convert_to_seconds(milliseconds: int) -> Tuple[str, str]:
    """
    This function converts video duration from milliseconds to seconds and minutes.
    param: milliseconds -> video duration in milliseconds
    returns: (seconds_str, minutes_str) — both zero-padded to at least 2 digits
    """
    total_seconds = int(milliseconds / 1000)
    seconds = total_seconds % 60
    minutes = total_seconds // 60
    return f"{seconds:02d}", f"{minutes:02d}"

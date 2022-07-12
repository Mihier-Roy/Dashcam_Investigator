from pathlib import Path


def get_file_count(input_path: Path) -> int:
    file_count = 0
    for item in input_path.rglob("*"):
        if item.is_file():
            file_count += 1

    return file_count

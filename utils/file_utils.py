import os
from typing import Set

def load_custom_ignores(ignore_file: str) -> Set[str]:
    """
    Load custom ignore patterns from file.
    Returns a set of absolute paths.
    """
    if os.path.exists(ignore_file):
        with open(ignore_file) as file:
            return {line.strip() for line in file if line.strip()}
    return set()

def save_custom_ignores(ignore_file: str, ignores: Set[str]) -> None:
    """
    Save custom ignore patterns to file.
    """
    os.makedirs(os.path.dirname(ignore_file), exist_ok=True)
    with open(ignore_file, 'w') as file:
        for ignore in sorted(ignores):
            file.write(f"{ignore}\n")

def get_relative_path(base_path: str, file_path: str) -> str:
    """
    Get the relative path of a file from the base path.
    """
    return os.path.relpath(file_path, base_path) 
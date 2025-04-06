import os
import sys
from utils.file_utils import load_custom_ignores, save_custom_ignores

def add_to_ignore(file_path: str, ignore_file: str) -> None:
    """
    Add a file or directory to the ignore list.
    """
    # Convert to absolute path
    abs_path = os.path.abspath(file_path)
    
    # Load existing ignores
    ignores = load_custom_ignores(ignore_file)
    
    # Add new path
    ignores.add(abs_path)
    
    # Save updated ignores
    save_custom_ignores(ignore_file, ignores)
    
    print(f"Added to ignore list: {abs_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_to_ignore.py <file_or_directory>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    ignore_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ignore_list.txt")
    
    add_to_ignore(file_path, ignore_file) 
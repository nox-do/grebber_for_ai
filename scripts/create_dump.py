import os
import sys
from typing import List

from detectors.language_detector import detect_language
from detectors.filter import FileFilter
from detectors.languages import LANGUAGES
from utils.file_utils import load_custom_ignores, get_relative_path
from utils.comment_utils import get_file_comment, ensure_file_comment

def create_dump(directory: str, ignore_file: str) -> None:
    """
    Create a dump.txt file containing all relevant code files from the directory.
    """
    # Detect language
    language_key = detect_language(directory)
    if not language_key:
        print("No supported programming language detected in the directory.")
        return

    # Load custom ignores
    custom_ignores = load_custom_ignores(ignore_file)
    
    # Filter files
    file_filter = FileFilter(custom_ignores)
    code_files = file_filter.filter_directory(directory)
    
    # Create dump.txt
    dump_path = os.path.join(directory, "dump.txt")
    with open(dump_path, "w", encoding="utf-8") as dump_file:
        for file_path in sorted(code_files):
            # Skip if file doesn't match language extensions
            if not any(file_path.endswith(ext) for ext in LANGUAGES[language_key].extensions):
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as source_file:
                    content = source_file.read()
                    
                # Add file comment
                rel_path = get_relative_path(directory, file_path)
                comment = get_file_comment(rel_path, language_key)
                content = ensure_file_comment(content, comment)
                
                # Write to dump file
                dump_file.write(content)
                dump_file.write("\n\n")
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_dump.py <directory>")
        sys.exit(1)
        
    directory = sys.argv[1]
    ignore_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ignore_list.txt")
    
    create_dump(directory, ignore_file) 
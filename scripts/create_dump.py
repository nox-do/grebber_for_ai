import os
import sys
from typing import List, Dict
from pathlib import Path

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from detectors.language_detector import detect_language
from utils.config_manager import ConfigManager
from utils.file_utils import get_relative_path
from utils.comment_utils import get_file_comment, ensure_file_comment

def create_dump(directory: str) -> None:
    """
    Create a dump.txt file containing all relevant code files from the directory.
    
    The function uses the following for file filtering:
    1. Standard ignore patterns (built-in)
    2. Custom ignore patterns (from .dump_config)
    3. .gitignore patterns (if a .gitignore file exists)
    4. Explicitly ignored paths (from .dump_config)
    """
    # Initialize config manager
    config_manager = ConfigManager(directory)
    
    # Detect language
    language_key, detected_languages = detect_language(directory)
    if not language_key:
        print("No supported programming language detected in the directory.")
        return
        
    # Update language info in config
    config_manager.update_language_info(language_key, detected_languages)
    
    # Clean ignore list (remove non-existent paths)
    config_manager.clean_ignore_list()
    
    # Get language settings
    lang_settings = config_manager.get_language_settings(language_key)
    if not lang_settings:
        print(f"Language settings not found for {language_key}")
        return
        
    # Get output settings
    output_settings = config_manager.get_output_settings()
    
    # Create dump.txt
    dump_path = os.path.join(directory, "dump.txt")
    with open(dump_path, "w", encoding="utf-8") as dump_file:
        # Walk through directory
        for root, dirs, files in os.walk(directory):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not config_manager.is_ignored(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip ignored files
                if config_manager.is_ignored(file_path):
                    continue
                    
                # Skip if file doesn't match language extensions
                if not any(file.endswith(ext) for ext in lang_settings['extensions']):
                    continue
                    
                try:
                    # Check file size
                    file_size = os.path.getsize(file_path)
                    if file_size > output_settings['max_file_size']:
                        print(f"Skipping {file_path}: File too large ({file_size} bytes)")
                        continue
                        
                    with open(file_path, "r", encoding="utf-8") as source_file:
                        content = source_file.read()
                        
                    # Add file comment if enabled
                    if output_settings['include_file_headers']:
                        rel_path = get_relative_path(directory, file_path)
                        comment = get_file_comment(rel_path, language_key)
                        content = ensure_file_comment(content, comment)
                        
                    # Add line numbers if enabled
                    if output_settings['include_line_numbers']:
                        lines = content.splitlines()
                        content = "\n".join(f"{i+1:4d} | {line}" for i, line in enumerate(lines))
                        
                    # Write to dump file
                    dump_file.write(content)
                    dump_file.write("\n\n")
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    # Update last dump time
    config_manager.update_last_dump_time()
    print(f"Dump created successfully at {dump_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_dump.py <directory>")
        sys.exit(1)
        
    directory = sys.argv[1]
    create_dump(directory) 
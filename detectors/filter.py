import os
from fnmatch import fnmatch
from typing import Set, List
from .languages import IGNORE_PATTERNS

class FileFilter:
    def __init__(self, custom_ignores: Set[str]):
        self.custom_ignores = custom_ignores

    def should_ignore(self, path: str) -> bool:
        """
        Check if a file or directory should be ignored based on patterns and custom ignores.
        """
        name = os.path.basename(path)
        abs_path = os.path.abspath(path)

        # Check standard patterns on filename
        if any(fnmatch(name, pattern) for pattern in IGNORE_PATTERNS):
            return True

        # Check exact absolute paths (Custom-Ignores)
        if abs_path in self.custom_ignores:
            return True

        return False

    def filter_directory(self, directory: str) -> List[str]:
        """
        Walk through directory and return list of files that should not be ignored.
        """
        code_files = []
        
        for root, dirs, files in os.walk(directory):
            # Filter directories (using absolute paths)
            dirs[:] = [
                d for d in dirs 
                if not self.should_ignore(os.path.join(root, d))
            ]
            
            # Filter files
            for file in files:
                file_path = os.path.join(root, file)
                if not self.should_ignore(file_path):
                    code_files.append(file_path)
                    
        return code_files 
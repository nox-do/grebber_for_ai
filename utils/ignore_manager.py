import os
from pathlib import Path
from typing import Set, List

class IgnoreManager:
    """Manages local .dump_ignore files for project directories."""
    
    IGNORE_FILENAME = ".dump_ignore"
    
    def __init__(self, directory: str):
        """Initialize the ignore manager for a directory."""
        self.directory = Path(directory).resolve()
        self.ignore_path = self.directory / self.IGNORE_FILENAME
        self.ignored_paths = self._load_ignored_paths()
    
    def _load_ignored_paths(self) -> Set[str]:
        """Load ignored paths from .dump_ignore file."""
        if self.ignore_path.exists():
            with open(self.ignore_path, 'r', encoding='utf-8') as f:
                return {line.strip() for line in f if line.strip() and not line.startswith('#')}
        return set()
    
    def save_ignored_paths(self) -> None:
        """Save ignored paths to .dump_ignore file."""
        # Only create the file if there are paths to ignore
        if not self.ignored_paths:
            return
            
        with open(self.ignore_path, 'w', encoding='utf-8') as f:
            f.write("# Local ignore patterns for dump.txt creation\n")
            f.write("# Each line represents a file or directory to ignore\n\n")
            for path in sorted(self.ignored_paths):
                f.write(f"{path}\n")
    
    def _normalize_path(self, path: str) -> str:
        """Normalize a path to a consistent format.
        
        This ensures that paths are stored in a consistent format, making it easier
        to detect duplicates.
        """
        # Convert to Path object
        path_obj = Path(path)
        
        # If path is not absolute, make it absolute relative to the directory
        if not path_obj.is_absolute():
            path_obj = (self.directory / path_obj).resolve()
        else:
            path_obj = path_obj.resolve()
            
        # Always store paths relative to the project directory
        try:
            rel_path = path_obj.relative_to(self.directory)
            return str(rel_path).replace('\\', '/')
        except ValueError:
            # If the path is outside the project directory, store it as absolute
            return str(path_obj).replace('\\', '/')
    
    def add_path(self, path: str) -> None:
        """Add a path to the ignore list."""
        normalized_path = self._normalize_path(path)
        if normalized_path not in self.ignored_paths:
            self.ignored_paths.add(normalized_path)
            self.save_ignored_paths()
    
    def is_ignored(self, path: str) -> bool:
        """Check if a path should be ignored."""
        normalized_path = self._normalize_path(path)
        
        # Check if the normalized path is in the ignore list
        if normalized_path in self.ignored_paths:
            return True
            
        # Check if any parent directory is in the ignore list
        path_parts = Path(normalized_path).parts
        current_path = ""
        for part in path_parts:
            if current_path:
                current_path = f"{current_path}/{part}"
            else:
                current_path = part
            if current_path in self.ignored_paths:
                return True
                
        return False 
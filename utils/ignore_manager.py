# --- START OF FILE utils/ignore_manager.py ---
import os
from pathlib import Path
from typing import Set, List

# Importiere den Error Logger, der ebenfalls den .dump Ordner kennt
from .error_logger import log_error

class IgnoreManager:
    """
    Manages the local .dump_ignore file, now located inside the .dump directory
    at the project root. Handles paths relative to the project root.
    """

    IGNORE_FILENAME = ".dump_ignore"
    DUMP_SUBDIR = ".dump" # Define the subdirectory name

    def __init__(self, directory: str):
        """
        Initialize the ignore manager for a project directory.
        Args:
            directory: The absolute path to the project root directory.
        """
        self.directory = Path(directory).resolve() # This is the project root
        # Path to the .dump directory within the project root
        self.dump_dir_path = self.directory / self.DUMP_SUBDIR
        # Path to the ignore file inside the .dump directory
        self.ignore_path = self.dump_dir_path / self.IGNORE_FILENAME
        # Load paths initially
        self.ignored_paths = self._load_ignored_paths()

    def _ensure_dump_dir_exists(self):
        """Creates the .dump directory if it doesn't exist."""
        try:
            # Create the .dump directory (and any parent, though unlikely needed here)
            # exist_ok=True prevents an error if the directory already exists
            self.dump_dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # Log an error if directory creation fails, but maybe loading still works
            log_error(str(self.directory), f"Warning: Failed to create dump directory {self.dump_dir_path} for ignore file: {e}")

    def _load_ignored_paths(self) -> Set[str]:
        """Load ignored relative paths from .dump/.dump_ignore file."""
        # No need to ensure dir exists just for loading, check file existence first
        if self.ignore_path.exists():
            try:
                with open(self.ignore_path, 'r', encoding='utf-8') as f:
                    # Normalize paths on load: use forward slashes, strip whitespace and surrounding slashes
                    return {
                        line.strip().replace('\\', '/').strip('/')
                        for line in f
                        if line.strip() and not line.startswith('#')
                    }
            except Exception as e:
                # Log error if loading fails
                log_error(str(self.directory), f"Failed to load ignore file {self.ignore_path}: {e}")
                return set()
        # Return empty set if file doesn't exist
        return set()

    def save_ignored_paths(self) -> None:
        """Save ignored relative paths to .dump/.dump_ignore file."""
        # If the set is empty, remove the file if it exists
        if not self.ignored_paths:
            if self.ignore_path.exists():
                try:
                    self.ignore_path.unlink() # Delete the file
                except Exception as e:
                     log_error(str(self.directory), f"Failed to delete empty ignore file {self.ignore_path}: {e}")
            return # Nothing more to do if the set is empty

        # Ensure the .dump directory exists before writing the file
        self._ensure_dump_dir_exists()
        try:
            # Write the ignored paths to the file
            with open(self.ignore_path, 'w', encoding='utf-8') as f:
                f.write("# Local ignore patterns relative to project root\n")
                f.write("# Use forward slashes (/), no leading/trailing slashes.\n\n")
                # Write paths sorted alphabetically
                for path in sorted(list(self.ignored_paths)):
                    f.write(f"{path}\n")
        except Exception as e:
            # Log error if saving fails
            log_error(str(self.directory), f"Failed to save ignore file {self.ignore_path}: {e}")

    def _normalize_relative_path(self, path: str) -> str:
        """
        Normalizes a path assumed to be relative to the manager's directory (project root).
        Ensures forward slashes and removes leading/trailing slashes.
        """
        # Strip whitespace, replace backslashes with forward slashes, remove surrounding slashes
        return path.strip().replace('\\', '/').strip('/')

    def add_path(self, relative_path: str) -> None:
        """
        Add a path (relative to project root) to the ignore list.
        The path is normalized before adding.
        """
        normalized_path = self._normalize_relative_path(relative_path)
        # Add only if the normalized path is not empty and not already present
        if normalized_path and normalized_path not in self.ignored_paths:
            self.ignored_paths.add(normalized_path)
            self.save_ignored_paths() # Save changes to the file
        elif not normalized_path:
             log_error(str(self.directory), f"Attempted to add an empty or invalid relative path to {self.ignore_path}")


    def is_ignored(self, relative_path_to_check: str) -> bool:
        """
        Check if a path (relative to the project root) should be ignored.
        The input path MUST be relative and normalized (forward slashes, no surrounding slashes).
        """
        normalized_path = self._normalize_relative_path(relative_path_to_check)

        if not normalized_path:
            return False # Ignore checks for empty paths

        # 1. Check for exact match in the set of ignored paths
        if normalized_path in self.ignored_paths:
            return True

        # 2. Check if any parent directory of the path is explicitly ignored
        #    Example: if 'src/components' is ignored, then 'src/components/button.py' should be ignored.
        try:
            # Use Path object to easily get parent parts
            path_obj = Path(normalized_path)
            # Iterate through parent parts: "part1", "part1/part2", ... up to the full path excluding the last part
            # e.g., for "a/b/c", check "a", then "a/b"
            if len(path_obj.parts) > 1:
                 for i in range(1, len(path_obj.parts)):
                     # Construct parent path string
                     parent_path_str = "/".join(path_obj.parts[:i])
                     # Check if this constructed parent path is in the ignored set
                     if parent_path_str in self.ignored_paths:
                         return True
        except Exception as e:
            # Log unexpected errors during path parsing or checking
            log_error(str(self.directory), f"Error checking parent ignore status for '{normalized_path}' in {self.ignore_path}: {e}")
            # Potentially return True here to be safe? Or False? Let's return False and log.
            return False

        # If neither exact match nor parent match found, it's not ignored by this manager
        return False
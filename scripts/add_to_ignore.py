# scripts/add_to_ignore.py (ÜBERARBEITET)

import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path - BEIBEHALTEN wegen Kontextmenü-Ausführung
# Annahme: Das Skript liegt in /scripts, Projekt-Root ist eine Ebene höher.
project_root_script_location = Path(__file__).parent.parent
sys.path.append(str(project_root_script_location))

try:
    from utils.config_manager import ConfigManager
    # Importiere den Error Logger (Pfad relativ zum project_root_script_location)
    from utils.error_logger import log_error
except ImportError as e:
    print(f"Error: Could not import necessary modules. Ensure the script is run correctly within the project structure.")
    print(f"Details: {e}")
    # Fallback logger if imports fail early
    def log_error(directory, message): print(f"Fallback Log in {directory}: {message}")
    # Exit here as core functionality is missing
    sys.exit(1)


def find_project_root(start_path: Path) -> Path:
    """
    Find the project root directory by looking upwards for .git or .dump_config.
    Raises FileNotFoundError if no root marker is found up to the filesystem root.
    """
    current = start_path.resolve()
    
    # If the start_path is a file, start from its parent directory
    if current.is_file():
        current = current.parent
    
    # Check current directory first
    if (current / '.git').exists() or (current / '.dump_config').exists():
        return current

    # Then check parent directories
    while current != current.parent:  # Stop at filesystem root
        current = current.parent
        if (current / '.git').exists() or (current / '.dump_config').exists():
            return current

    # If no marker found up to the root
    raise FileNotFoundError(f"Could not find project root (.git or .dump_config) starting from {start_path}")

def add_single_path_to_ignore(file_or_dir_path: str, globally: bool) -> None:
    """
    Adds a single file or directory path to the appropriate ignore list.

    Args:
        file_or_dir_path: The path string of the item to ignore (can be relative to CWD or absolute).
        globally: True to add to global list, False for local list relative to project root.
    """
    project_root: Optional[Path] = None # Initialize for logging in case of early error
    log_dir_fallback = str(Path.cwd()) # Fallback logging directory

    try:
        # 1. Resolve the input path to an absolute path
        path_to_add = Path(file_or_dir_path)
        if not path_to_add.is_absolute():
             # If run from context menu, CWD might be weird. Assume path is relative to CWD
             # or it's an absolute path provided.
            path_to_add = Path.cwd() / path_to_add
        abs_path = path_to_add.resolve() # Ensure it's resolved and clean

        # Check if path actually exists (optional, but good practice)
        if not abs_path.exists():
            print(f"Warning: Path does not exist: {abs_path}. Adding it anyway.")
            # log_error? Maybe not, user might intend to ignore a path before creating it.

        # 2. Find the project root, starting from the directory containing the item
        #    or the item itself if it's a directory.
        search_start_dir = abs_path.parent if abs_path.is_file() else abs_path
        project_root = find_project_root(search_start_dir)
        log_dir_fallback = str(project_root) # Use project root for logging once found

        # 3. Initialize ConfigManager
        config_manager = ConfigManager(str(project_root))

        # 4. Handle Global Ignore
        if globally:
            abs_path_str = str(abs_path)
            if abs_path_str in config_manager.get_ignored_paths():
                print(f"Path already in global ignore list (.dump_config): {abs_path_str}")
                return

            config_manager.add_to_ignore(abs_path_str, globally=True)
            print(f"Added to global ignore list (.dump_config): {abs_path_str}")
            print(f"Config file: {config_manager.config_path}")

        # 5. Handle Local Ignore
        else:
            try:
                # Calculate the path relative to the project root
                rel_path = abs_path.relative_to(project_root)
                # Normalize: forward slashes, strip surrounding slashes
                rel_path_str = str(rel_path).replace('\\', '/').strip('/')

                if not rel_path_str: # Ignore if it results in an empty string (e.g., ignoring the root itself locally?)
                     print(f"Cannot add project root directory itself to local ignore list.")
                     return

                # Check if this specific relative path is already in .dump_ignore
                # We access the manager directly for this check for clarity
                if config_manager.local_ignore.is_ignored(rel_path_str):
                     # Check if it was ignored directly or via parent
                     if rel_path_str in config_manager.local_ignore.ignored_paths:
                         print(f"Path already explicitly in local ignore list (.dump_ignore): {abs_path} (as '{rel_path_str}')")
                     else:
                         print(f"Path is already covered by a parent entry in local ignore list (.dump_ignore): {abs_path} (covered by pattern matching '{rel_path_str}')")
                     return

                # Add the normalized relative path
                config_manager.add_to_ignore(rel_path_str, globally=False)
                print(f"Added to local ignore list (.dump_ignore): {abs_path} (as '{rel_path_str}')")
                print(f"Ignore file: {config_manager.local_ignore.ignore_path}")

            except ValueError:
                # This happens if abs_path is not within project_root
                print(f"Error: Path {abs_path} is outside the project directory {project_root}. Cannot add to local ignore list (.dump_ignore).")
                log_error(str(project_root), f"Cannot add path {abs_path} to local ignore list: it is outside the project root {project_root}.")
            except Exception as e_local:
                 # Catch other potential errors during local add
                 print(f"Error adding path {abs_path} to local ignore list: {e_local}")
                 log_error(str(project_root), f"Error adding path {abs_path} as relative path to local ignore list: {e_local}")

    except FileNotFoundError as e_root:
        # Error from find_project_root
        print(f"Error: {e_root}")
        print("Could not determine the project's root directory. Please ensure you are running this command within a project containing a '.git' folder or a '.dump_config' file.")
        log_error(log_dir_fallback, f"Failed to find project root when adding '{file_or_dir_path}': {e_root}")
    except ImportError:
         # Already handled above, but catch again just in case.
         print("Error: Core modules could not be imported.")
         sys.exit(1)
    except Exception as e_main:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e_main}")
        log_dir = str(project_root) if project_root else log_dir_fallback
        log_error(log_dir, f"Unexpected error in add_single_path_to_ignore for '{file_or_dir_path}', globally={globally}: {e_main}")
        # Optional: Exit with error code?
        # sys.exit(1)


if __name__ == "__main__":
    # Argument parsing needs refinement if multiple paths can be passed via context menu
    # Assuming for now it's called with one path and optional --global flag

    args = sys.argv[1:]
    if not args:
        print("Usage: python add_to_ignore.py <file_or_directory> [--global]")
        sys.exit(1)

    # Determine if --global is present
    globally = "--global" in args

    # Find the path argument (assume it's the first argument that isn't '--global')
    path_arg = None
    for arg in args:
        if arg != "--global":
            path_arg = arg
            break

    if path_arg is None:
        print("Error: No file or directory path specified.")
        print("Usage: python add_to_ignore.py <file_or_directory> [--global]")
        sys.exit(1)

    # Call the main function
    add_single_path_to_ignore(path_arg, globally=globally)

    # Add a small pause if run from context menu? Sometimes useful for user to see output.
    # import time
    # print("\nOperation finished. Closing in 3 seconds...")
    # time.sleep(3)
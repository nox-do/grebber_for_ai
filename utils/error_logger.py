# --- START OF FILE utils/error_logger.py ---

import os
from datetime import datetime
from pathlib import Path
from typing import Optional # Import Optional

LOG_FILENAME = "dump_error.log"
DUMP_SUBDIR = ".dump" # Define the subdirectory name consistent with other managers

def log_error(directory: str, message: str):
    """
    Logs an error message to dump_error.log inside the .dump subdirectory
    of the specified project directory.

    Args:
        directory: The project's root directory path string.
        message: The error message to log.
    """
    # --- Initialize variables before the try block ---
    dump_dir: Optional[Path] = None
    log_path: Optional[Path] = None
    # --- End Initialization ---

    try:
        # 1. Resolve the base directory (should be the project root)
        project_dir = Path(directory).resolve()

        # 2. Define the path to the .dump subdirectory
        dump_dir = project_dir / DUMP_SUBDIR # Assign the actual Path object

        # 3. Ensure the .dump directory exists
        try:
            # dump_dir is guaranteed to be assigned here if this code is reached
            dump_dir.mkdir(parents=True, exist_ok=True)
        except Exception as mkdir_e:
            # Log the error related to directory creation, but we might still proceed
            # if the directory potentially exists despite the error.
            print(f"!!! WARNING: Failed to ensure log directory exists {dump_dir}: {mkdir_e}")
            # The open() call later will fail definitively if the dir is unusable.

        # 4. Define the full path to the log file
        # dump_dir is guaranteed to be assigned here
        log_path = dump_dir / LOG_FILENAME # Assign the actual Path object

        # 5. Get timestamp and format the log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] ERROR: {message}\n"

        # 6. Append the log entry to the file
        # log_path is guaranteed to be assigned here
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

    except Exception as e:
        # Critical error if logging itself fails for any reason
        print(f"!!! CRITICAL: Failed to write to error log file.")
        # --- Safely construct the intended path string for the error message ---
        intended_path_str = "Unknown"
        if log_path: # Check if log_path got assigned
            intended_path_str = str(log_path)
        elif dump_dir: # Check if dump_dir got assigned (implies log_path calculation failed)
            intended_path_str = f"{str(dump_dir)}/{LOG_FILENAME} (Path calculation failed)"
        # --- End Safe Construction ---
        print(f"    Intended log path: {intended_path_str}")
        print(f"    Logging Error: {e}")
        print(f"    Original error message: {message}")

# --- END OF FILE utils/error_logger.py ---
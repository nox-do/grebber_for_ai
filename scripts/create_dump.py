# --- START OF FILE scripts/create_dump.py ---
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root_script_location = Path(__file__).parent.parent
sys.path.insert(0, str(project_root_script_location))

try:
    from detectors.language_detector import detect_language
    from utils.config_manager import ConfigManager
    from utils.file_utils import get_relative_path
    # comment_utils are not directly used anymore for header generation
    # from utils.comment_utils import get_file_comment, ensure_file_comment
    from utils.error_logger import log_error
except ImportError as e:
    print(f"Error: Could not import necessary modules. Ensure the script is run correctly.")
    print(f"Details: {e}")
    def log_error(directory, message): print(f"Fallback Log in {directory}: {message}")
    sys.exit(1)

def create_dump(directory: str) -> None:
    """
    Create a dump.txt file containing relevant code files from the directory.
    Assumes 'directory' is the root of the project. Generated config/log files
    will be placed inside a '.dump' subdirectory within this root.
    """
    project_dir_path = Path(directory).resolve()
    log_dir = str(project_dir_path) # Base directory for logging context

    try:
        # Initialize config manager (will handle .dump subdirectory internally)
        print(f"Initializing ConfigManager for project root: {project_dir_path}")
        config_manager = ConfigManager(str(project_dir_path))

    except Exception as e_cfg_init:
        print(f"Fatal Error: Failed to initialize ConfigManager for directory '{directory}'. Cannot proceed.")
        # Use log_dir which is project_dir_path here, as config_manager might not be fully initialized
        log_error(log_dir, f"Fatal Error initializing ConfigManager: {e_cfg_init}")
        sys.exit(1)

    try:
        # Detect language
        print("Detecting language...")
        language_key, detected_languages = detect_language(str(project_dir_path))
        if not language_key:
            print("Warning: No supported primary programming language detected.")
            log_error(log_dir, "Language detection did not identify a primary language.")
        else:
            print(f"Detected primary language: {language_key}")
            config_manager.update_language_info(language_key, detected_languages)

        # Clean global ignore list
        print("Cleaning global ignore list (removing non-existent paths)...")
        config_manager.clean_ignore_list()

        # Get language and output settings
        lang_settings = config_manager.get_language_settings(language_key) if language_key else None
        output_settings = config_manager.get_output_settings()

        print(f"Output settings: Headers={output_settings['include_file_headers']}, LineNumbers={output_settings['include_line_numbers']}, MaxSize={output_settings['max_file_size']}")
        if not output_settings['include_line_numbers']:
             print("Line numbers will not be included in the dump.")

        # Dump file path (remains in the project root)
        dump_path = project_dir_path / "dump.txt"
        print(f"Creating dump file at: {dump_path}")

        # --- File Collection and Writing ---
        total_files_processed = 0
        total_files_dumped = 0
        try:
            with open(dump_path, "w", encoding="utf-8") as dump_file:
                # Walk through the project directory
                for root, dirs, files in os.walk(str(project_dir_path)):
                    current_root_path = Path(root).resolve()

                    # Filter ignored directories before recursing
                    original_dirs = dirs[:]
                    dirs[:] = []
                    for d in original_dirs:
                        dir_path_abs = current_root_path / d
                        if not config_manager.is_ignored(str(dir_path_abs)):
                             dirs.append(d)
                        # else: print(f"Ignoring directory: {dir_path_abs}") # Optional

                    # Process files in the current directory
                    for file in files:
                        total_files_processed += 1
                        file_path_abs = current_root_path / file
                        file_path_str = str(file_path_abs)

                        # 1. Skip ignored files/dirs based on ConfigManager rules
                        if config_manager.is_ignored(file_path_str):
                            continue

                        # 2. Skip if language detected and file doesn't match extensions
                        # ----- START OF MODIFICATION -----
                        # We DON'T filter by extension anymore based on detected language.
                        # Language detection is primarily used for setting the correct comment prefix in headers.
                        # File exclusion should be managed solely by the ignore rules handled by ConfigManager.
                        # if lang_settings and 'extensions' in lang_settings:
                        #     if not any(file.lower().endswith(ext.lower()) for ext in lang_settings['extensions']):
                        #         continue
                        # elif language_key and not lang_settings:
                        #     # Language detected, but no settings found - don't filter by extension
                        #     log_error(log_dir, f"Language '{language_key}' detected but settings missing, not filtering by extension.")
                        #     pass # Proceed without extension filtering
                        # ----- END OF MODIFICATION -----

                        try:
                            # 3. Check file size
                            file_size = file_path_abs.stat().st_size
                            if file_size > output_settings['max_file_size']:
                                print(f"Skipping file (too large: {file_size} bytes > {output_settings['max_file_size']}): {file_path_str}")
                                log_error(log_dir, f"Skipped large file {file_path_str} ({file_size} bytes)")
                                continue

                            # 4. Read file content
                            with open(file_path_abs, "r", encoding="utf-8") as source_file:
                                content = source_file.read()

                            # 5. Generate file header (if enabled)
                            header = ""
                            if output_settings['include_file_headers']:
                                try:
                                    rel_path_for_header = get_relative_path(str(project_dir_path), file_path_str).replace('\\', '/')

                                    # Determine comment prefix based on detected language
                                    comment_prefix = "#" # Default comment prefix
                                    if lang_settings and lang_settings.get('comment_prefix'):
                                        comment_prefix = lang_settings['comment_prefix']
                                    elif language_key:
                                        # If language was detected but settings (incl. comment_prefix) are missing
                                        log_error(log_dir, f"Comment prefix missing for language '{language_key}', using default '#'.")
                                    # If no language was detected (language_key is None), default '#' is used.

                                    header = f"{comment_prefix} FILE: {rel_path_for_header}\n\n"

                                except ValueError as e_relpath:
                                     print(f"Warning: Could not get relative path for file header: {file_path_str}. Error: {e_relpath}")
                                     log_error(log_dir, f"Failed to get relative path for header for {file_path_str}: {e_relpath}")
                                     header = f"# FILE: {file_path_abs.name} (error getting relative path)\n\n" # Fallback header
                                except Exception as e_header:
                                     print(f"Warning: Could not generate header for file: {file_path_str}. Error: {e_header}")
                                     log_error(log_dir, f"Failed to generate header for {file_path_str}: {e_header}")
                                     header = f"# FILE: {file_path_abs.name} (error generating header)\n\n" # Fallback header

                            # 6. Combine header and content (No line numbers logic here anymore, as per config default/value)
                            processed_content = f"{header}{content}"

                            # 7. Write to dump file
                            dump_file.write(processed_content)
                            dump_file.write("\n\n---\n\n") # File separator
                            total_files_dumped += 1

                        except OSError as e_os:
                             print(f"Error processing file {file_path_str} (OS Error): {e_os}")
                             log_error(log_dir, f"OS Error processing file {file_path_str}: {e_os}")
                        except UnicodeDecodeError as e_unicode:
                             print(f"Error processing file {file_path_str} (Encoding Error): Likely not UTF-8. Skipping.")
                             log_error(log_dir, f"Encoding Error (not UTF-8?) processing file {file_path_str}: {e_unicode}")
                        except Exception as e_file:
                            print(f"Error processing file {file_path_str}: {e_file}")
                            log_error(log_dir, f"Failed processing file {file_path_str}: {e_file}")

        except IOError as e_dump:
            print(f"Fatal Error: Could not write to dump file {dump_path}: {e_dump}")
            log_error(log_dir, f"Fatal Error writing to dump file {dump_path}: {e_dump}")
            sys.exit(1)

        # Update last dump time
        config_manager.update_last_dump_time()

        print(f"\nDump creation finished.")
        print(f"  Processed: {total_files_processed} files found")
        print(f"  Included in dump: {total_files_dumped} files")
        print(f"  Dump file location: {dump_path}")

        # Check if errors were logged in the new location
        error_log_path = project_dir_path / ConfigManager.DUMP_SUBDIR / "dump_error.log"
        if error_log_path.exists():
             print(f"  NOTE: Errors occurred during the process. See {error_log_path} for details.")


    except Exception as e_main:
        print(f"An unexpected error occurred during dump creation: {e_main}")
        # Use log_dir, as config_manager might not be fully available if error happened early
        log_error(log_dir, f"Unexpected error in create_dump for directory '{directory}': {e_main}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_dump.py <directory>")
        print("  <directory>: The root directory of the project to dump.")
        sys.exit(1)

    target_directory = sys.argv[1]

    if not os.path.isdir(target_directory):
         print(f"Error: Provided path '{target_directory}' is not a valid directory.")
         sys.exit(1)

    create_dump(target_directory)

# --- END OF FILE scripts/create_dump.py ---
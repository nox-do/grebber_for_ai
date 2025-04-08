import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.config_manager import ConfigManager
from utils.ignore_manager import IgnoreManager

def find_project_root(start_path: Path) -> Path:
    """Find the project root directory by looking for .git or .dump_config"""
    current = start_path
    while current != current.parent:  # Until we reach the root
        if (current / '.git').exists() or (current / '.dump_config').exists():
            return current
        current = current.parent
    return start_path.parent  # Fallback to parent directory if no markers found

def add_to_ignore(file_path: str, globally: bool = False) -> None:
    """
    Add a file or directory to the ignore list.
    
    Args:
        file_path: Path to the file or directory to ignore
        globally: If True, add to global config, otherwise add to local .dump_ignore
    """
    # Convert to absolute path
    file_path = Path(file_path)
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    file_path = file_path.resolve()
    
    # Get the target directory
    target_dir = Path.cwd()
    
    if globally:
        # For global ignore, use the project root
        project_dir = find_project_root(file_path)
        config_manager = ConfigManager(str(project_dir))
        
        # Check if already ignored
        if str(file_path) in config_manager.get_ignored_paths():
            print(f"Path already in global ignore list: {file_path}")
            return
            
        # Add to global ignore list
        config_manager.add_to_ignore(str(file_path), globally=True)
        print(f"Added to global ignore list: {file_path}")
    else:
        # For local ignore, use the target directory
        ignore_manager = IgnoreManager(str(target_dir))
        
        # Check if already ignored
        try:
            rel_path = file_path.name if file_path.is_file() else file_path.relative_to(target_dir)
            if ignore_manager.is_ignored(str(rel_path)):
                print(f"Path already in local ignore list: {file_path}")
                return
                
            # Add to local ignore list
            ignore_manager.add_path(str(rel_path))
            print(f"Added to local ignore list: {file_path}")
        except ValueError:
            print(f"Error: {file_path} is not within the target directory {target_dir}")
            return

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_to_ignore.py <file_or_directory> [--global]")
        sys.exit(1)
        
    file_path = sys.argv[1]
    globally = "--global" in sys.argv[2:] if len(sys.argv) > 2 else False
    
    add_to_ignore(file_path, globally=globally) 
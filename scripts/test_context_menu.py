import os
import sys
import random
import string
import shutil
from pathlib import Path

# Add parent directory to Python path to find our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.create_dump import create_dump
from scripts.add_to_ignore import add_to_ignore
from utils.config_manager import ConfigManager
from utils.ignore_manager import IgnoreManager

def create_random_string(length=8):
    """Create a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_test_environment():
    """Create a test environment with random files and directories."""
    try:
        # Create base test directory
        base_dir = Path("test_context_menu")
        if base_dir.exists():
            shutil.rmtree(base_dir)
        base_dir.mkdir()
        
        # Create a random subdirectory
        subdir_name = create_random_string()
        subdir = base_dir / subdir_name
        subdir.mkdir()
        
        # Create a random Python file in the subdirectory
        file_name = f"{create_random_string()}.py"
        file_path = subdir / file_name
        with open(file_path, "w", encoding='utf-8') as f:
            f.write("# Test Python file\nprint('Hello, World!')\n")
        
        # Create a lorem.txt file for testing
        lorem_path = subdir / "lorem.txt"
        with open(lorem_path, "w", encoding='utf-8') as f:
            f.write("Lorem ipsum dolor sit amet\n")
        
        return base_dir, subdir, file_path, lorem_path
    except Exception as e:
        print(f"Error creating test environment: {str(e)}")
        sys.exit(1)

def test_create_dump(directory):
    """Test the create_dump function directly."""
    try:
        print("\n=== Testing create_dump with %V ===")
        print(f"Directory: {directory}")
        
        create_dump(str(directory))
        
        dump_file = directory / "dump.txt"
        if dump_file.exists():
            print("✓ dump.txt created successfully")
            print(f"  Size: {dump_file.stat().st_size} bytes")
            return True
        else:
            print("✗ dump.txt was not created")
            return False
            
    except Exception as e:
        print(f"Error in create_dump: {str(e)}")
        return False

def test_add_to_ignore(path, globally=False):
    """Test the add_to_ignore function directly.
    
    Args:
        path: Path to the file or directory to ignore
        globally: Whether to add to global config or local .dump_ignore
    """
    try:
        ignore_type = "global" if globally else "local"
        print(f"\n=== Testing add_to_ignore ({ignore_type}) with %L ===")
        print(f"Path: {path}")
        
        # Get the project directory and absolute path
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj
        path_obj = path_obj.resolve()
        
        # For local ignore, use the base directory
        if globally:
            project_dir = Path(os.path.dirname(path_obj))
        else:
            # Use the parent directory of the test directory
            project_dir = path_obj
            while project_dir.name != "test_context_menu":
                project_dir = project_dir.parent
                if project_dir == project_dir.parent:  # Reached root
                    project_dir = Path(os.path.dirname(path_obj))
                    break
        
        # Initialize managers
        config_manager = ConfigManager(str(project_dir))
        ignore_manager = IgnoreManager(str(project_dir))
        
        # Add to ignore list
        add_to_ignore(str(path), globally=globally)
        
        # Verify the result
        if globally:
            config_file = project_dir / ".dump_config"
            if config_file.exists():
                # For global ignore, check if the absolute path is in the config
                if str(path_obj) in config_manager.get_ignored_paths():
                    print(f"✓ Added to global ignore list successfully")
                    print(f"  Config exists at: {config_file}")
                    return True
                else:
                    print(f"✗ Failed to add to global ignore list")
                    return False
            else:
                print(f"✗ .dump_config file not found")
                return False
        else:
            ignore_file = project_dir / ".dump_ignore"
            if ignore_file.exists():
                # For local ignore, check if the relative path is in the ignore file
                with open(ignore_file, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    try:
                        rel_path = str(path_obj.relative_to(project_dir)).replace('\\', '/')
                        if rel_path in lines:
                            print(f"✓ Added to local ignore list successfully")
                            print(f"  Ignore file exists at: {ignore_file}")
                            return True
                        else:
                            print(f"✗ Failed to add to local ignore list")
                            return False
                    except ValueError as e:
                        print(f"✗ Failed to make path relative: {str(e)}")
                        return False
            else:
                print(f"✗ .dump_ignore file not found")
                return False
            
    except Exception as e:
        print(f"Error in add_to_ignore: {str(e)}")
        return False

def test_duplicate_ignore(path):
    """Test that adding the same path twice doesn't create duplicates."""
    try:
        print(f"\n=== Testing duplicate ignore entries ===")
        print(f"Path: {path}")
        
        # Get the project directory and absolute path
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj
        path_obj = path_obj.resolve()
        
        # Use the parent directory of the test directory
        project_dir = path_obj
        while project_dir.name != "test_context_menu":
            project_dir = project_dir.parent
            if project_dir == project_dir.parent:  # Reached root
                project_dir = Path(os.path.dirname(path_obj))
                break
        
        # Add to local ignore first
        add_to_ignore(str(path), globally=False)
        
        # Try to add again
        add_to_ignore(str(path), globally=False)
        
        # Check if the path is in the ignore list exactly once
        ignore_file = project_dir / ".dump_ignore"
        if ignore_file.exists():
            with open(ignore_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                try:
                    rel_path = str(path_obj.relative_to(project_dir)).replace('\\', '/')
                    count = sum(1 for line in lines if line == rel_path)
                    if count == 1:
                        print(f"✓ Path appears exactly once in local ignore list")
                        return True
                    else:
                        print(f"✗ Path appears {count} times in local ignore list")
                        return False
                except ValueError as e:
                    print(f"✗ Failed to make path relative: {str(e)}")
                    return False
        else:
            print(f"✗ .dump_ignore file not found")
            return False
            
    except Exception as e:
        print(f"Error in duplicate_ignore test: {str(e)}")
        return False

def main():
    """Run all tests."""
    try:
        print("=== Starting Context Menu Tests ===")
        print("\nCreating test environment...")
        base_dir, subdir, file_path, lorem_path = create_test_environment()
        
        print(f"\nTest environment created:")
        print(f"Base directory: {base_dir}")
        print(f"Subdirectory: {subdir}")
        print(f"Test file: {file_path}")
        print(f"Lorem file: {lorem_path}")
        
        # Test create_dump with directory
        success = test_create_dump(base_dir)
        
        # Test add_to_ignore with directory (local)
        success = test_add_to_ignore(subdir, globally=False) and success
        
        # Test add_to_ignore with file (local)
        success = test_add_to_ignore(file_path, globally=False) and success
        
        # Test add_to_ignore with lorem.txt (local)
        success = test_add_to_ignore(lorem_path, globally=False) and success
        
        # Test add_to_ignore with file (global)
        success = test_add_to_ignore(file_path, globally=True) and success
        
        # Test duplicate entries
        success = test_duplicate_ignore(lorem_path) and success
        
        print("\nCleaning up...")
        shutil.rmtree(base_dir)
        print("=== Test completed! ===")
        
        if not success:
            print("\nSome tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
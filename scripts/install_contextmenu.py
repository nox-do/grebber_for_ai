import os
import sys
import winreg
from typing import Tuple

def get_script_path(script_name: str) -> str:
    """Get the absolute path to a script."""
    return os.path.join(os.path.dirname(__file__), script_name)

def create_context_menu(key_path: str, command: str, menu_text: str) -> None:
    """Create a context menu entry in the Windows Registry."""
    try:
        # Create the key
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        
        # Create the command subkey
        command_key = winreg.CreateKey(key, "shell\\command")
        
        # Set the command value
        winreg.SetValue(command_key, "", winreg.REG_SZ, command)
        
        # Set the menu text
        winreg.SetValue(key, "", winreg.REG_SZ, menu_text)
        
        print(f"Created context menu: {menu_text}")
        
    except Exception as e:
        print(f"Error creating context menu: {str(e)}")
        raise

def install_context_menus() -> None:
    """Install the context menu entries."""
    # Get absolute paths to scripts
    scripts_dir = os.path.abspath(os.path.dirname(__file__))
    create_dump_script = os.path.join(scripts_dir, "create_dump.py")
    add_to_ignore_script = os.path.join(scripts_dir, "add_to_ignore.py")
    
    # Use global python
    python_exe = "python.exe"
    
    # Create the commands with global python and absolute paths
    create_dump_cmd = f'"{python_exe}" "{create_dump_script}" "%V"'
    add_to_ignore_cmd = f'"{python_exe}" "{add_to_ignore_script}" "%L"'
    
    # Create context menus for both files and directories
    create_context_menu(
        "Directory\\Background\\shell\\CreateDump",
        create_dump_cmd,
        "Create dump.txt"
    )
    
    # Add to ignore for files
    create_context_menu(
        "AllFilesystemObjects\\shell\\AddToIgnore",
        add_to_ignore_cmd,
        "Add to ignore for dump"
    )
    
    print("Context menu installation completed successfully!")

if __name__ == "__main__":
    install_context_menus() 
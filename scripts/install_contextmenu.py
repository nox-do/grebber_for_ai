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
    # Get absolute paths
    create_dump_script = get_script_path("create_dump.py")
    add_to_ignore_script = get_script_path("add_to_ignore.py")
    
    # Create the commands with sys.executable
    create_dump_cmd = f'"{sys.executable}" "{create_dump_script}" "%1"'
    add_to_ignore_cmd = f'"{sys.executable}" "{add_to_ignore_script}" "%1"'
    
    # Create context menus
    create_context_menu(
        "Directory\\shell\\CreateDump",
        create_dump_cmd,
        "Create dump.txt"
    )
    
    create_context_menu(
        "*\\shell\\AddToIgnore",
        add_to_ignore_cmd,
        "Add to ignore for dump"
    )
    
    print("Context menu installation completed successfully!")

if __name__ == "__main__":
    install_context_menus() 
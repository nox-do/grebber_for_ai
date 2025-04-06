import winreg

def delete_context_menu(key_path: str) -> None:
    """Delete a context menu entry from the Windows Registry."""
    try:
        # Delete the command subkey first
        command_key = f"{key_path}\\shell\\command"
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, command_key)
        
        # Delete the shell subkey
        shell_key = f"{key_path}\\shell"
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, shell_key)
        
        print(f"Removed context menu: {key_path}")
        
    except Exception as e:
        print(f"Error removing context menu: {str(e)}")
        raise

def uninstall_context_menus() -> None:
    """Remove the context menu entries."""
    # Remove context menus
    delete_context_menu("Directory\\shell\\CreateDump")
    delete_context_menu("*\\shell\\AddToIgnore")
    
    print("Context menu uninstallation completed successfully!")

if __name__ == "__main__":
    uninstall_context_menus() 
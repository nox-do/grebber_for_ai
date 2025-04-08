import winreg

def delete_context_menu(key_path: str) -> None:
    """Delete a context menu entry from the Windows Registry."""
    try:
        # Open the parent key
        parent_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path, 0, winreg.KEY_ALL_ACCESS)
        
        # Delete the command subkey first
        try:
            winreg.DeleteKey(parent_key, "shell\\command")
        except WindowsError:
            pass  # Key might not exist
            
        # Delete the shell subkey
        try:
            winreg.DeleteKey(parent_key, "shell")
        except WindowsError:
            pass  # Key might not exist
            
        # Close the parent key
        winreg.CloseKey(parent_key)
        
        print(f"Removed context menu: {key_path}")
        
    except Exception as e:
        print(f"Error removing context menu: {str(e)}")
        raise

def uninstall_context_menus() -> None:
    """Remove the context menu entries."""
    # Remove only the AddToIgnore context menu
    delete_context_menu("AllFilesystemObjects\\shell\\AddToIgnore")
    
    print("Context menu uninstallation completed successfully!")

if __name__ == "__main__":
    uninstall_context_menus() 
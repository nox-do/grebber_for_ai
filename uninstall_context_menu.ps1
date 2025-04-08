# PowerShell script to uninstall context menu entries
# This script must be run as administrator

# Function to remove a context menu entry
function Remove-ContextMenu {
    param (
        [string]$KeyPath
    )
    
    try {
        # Remove the key
        Remove-Item -Path "Registry::HKEY_CLASSES_ROOT\$KeyPath" -Recurse -Force
        Write-Host "Removed context menu: $KeyPath"
    }
    catch {
        Write-Host "Error removing context menu: $_"
    }
}

# Remove context menus
Write-Host "Uninstalling context menu entries..."

# Remove Create dump for directory background
Remove-ContextMenu -KeyPath "Directory\Background\shell\CreateDump"

Write-Host "Context menu uninstallation completed!"

# Pause at the end to see the output
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 
# PowerShell script to install context menu entries with administrator privileges
# This script must be run as administrator

# Get the absolute path to the script and project directory
$currentDir = Get-Location
$projectDir = $currentDir
$scriptsDir = Join-Path $projectDir "scripts"
$createDumpScript = Join-Path $scriptsDir "create_dump.py"
$addToIgnoreScript = Join-Path $scriptsDir "add_to_ignore.py"

# Convert to absolute path
$createDumpScript = [System.IO.Path]::GetFullPath($createDumpScript)
$addToIgnoreScript = [System.IO.Path]::GetFullPath($addToIgnoreScript)
$projectDir = [System.IO.Path]::GetFullPath($projectDir)

# Use specific Python path
$pythonExe = "C:\Users\Daniel\AppData\Local\Programs\Python\Python313\python.exe"

# Create the commands with specific Python path, absolute paths, and working directory
$createDumpCmd = "cmd /c `"cd /d `"$projectDir`" && `"$pythonExe`" `"$createDumpScript`" `"%V`"`""
$addToIgnoreLocalCmd = "cmd /c `"cd /d `"$projectDir`" && `"$pythonExe`" `"$addToIgnoreScript`" `"%L`"`""
$addToIgnoreGlobalCmd = "cmd /c `"cd /d `"$projectDir`" && `"$pythonExe`" `"$addToIgnoreScript`" `"%L`" --global`""

# Function to create a context menu entry
function Create-ContextMenu {
    param (
        [string]$KeyPath,
        [string]$Command,
        [string]$MenuText
    )
    
    try {
        # Create the key
        $key = New-Item -Path "Registry::HKEY_CLASSES_ROOT\$KeyPath" -Force
        
        # Set the menu text
        Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\$KeyPath" -Name "(default)" -Value $MenuText
        
        # Create the command subkey
        $commandKey = New-Item -Path "Registry::HKEY_CLASSES_ROOT\$KeyPath\command" -Force
        
        # Set the command value
        Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\$KeyPath\command" -Name "(default)" -Value $Command
        
        Write-Host "Created context menu: $MenuText"
        Write-Host "Command: $Command"
    }
    catch {
        Write-Host "Error creating context menu: $_"
    }
}

# Create context menus
Write-Host "Installing context menu entries..."

# Create dump for directory background
Create-ContextMenu -KeyPath "Directory\Background\shell\CreateDump" -Command $createDumpCmd -MenuText "Dump für AI erstellen"

# Create ignore submenu
$ignoreSubmenuKey = "AllFilesystemObjects\shell\DumpIgnore"
New-Item -Path "Registry::HKEY_CLASSES_ROOT\$ignoreSubmenuKey" -Force
Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\$ignoreSubmenuKey" -Name "(default)" -Value "Dump Ignore"
Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\$ignoreSubmenuKey" -Name "SubCommands" -Value ""
Set-ItemProperty -Path "Registry::HKEY_CLASSES_ROOT\$ignoreSubmenuKey" -Name "MUIVerb" -Value "Dump Ignore"

# Create local ignore option
Create-ContextMenu -KeyPath "$ignoreSubmenuKey\shell\LocalIgnore" -Command $addToIgnoreLocalCmd -MenuText "Ignore in this folder"

# Create global ignore option
Create-ContextMenu -KeyPath "$ignoreSubmenuKey\shell\GlobalIgnore" -Command $addToIgnoreGlobalCmd -MenuText "Ignore globally"

Write-Host "Context menu installation completed!"

# Pause at the end to see the output
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 
@echo off
echo Uninstalling Dump für AI erstellen Context Menu Tool...
powershell -Command "Start-Process -Verb RunAs -FilePath 'powershell.exe' -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0uninstall_context_menu.ps1\"'"
if %ERRORLEVEL% NEQ 0 (
    echo Uninstallation failed. Press any key to exit.
    pause > nul
) 
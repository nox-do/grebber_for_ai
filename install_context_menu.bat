@echo off
echo Running Dump für AI erstellen Context Menu Tool installation...
powershell -Command "Start-Process -Verb RunAs -FilePath 'powershell.exe' -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0install_context_menu.ps1\"'"
if %ERRORLEVEL% NEQ 0 (
    echo Installation failed. Press any key to exit.
    pause > nul
) 
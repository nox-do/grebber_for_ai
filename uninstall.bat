@echo off
echo Running Create Dump.txt Context Menu Tool uninstallation...
powershell -Command "Start-Process -Verb RunAs -FilePath 'py' -ArgumentList 'scripts/uninstall_contextmenu.py'"
echo Uninstallation completed. Press any key to exit.
pause > nul 
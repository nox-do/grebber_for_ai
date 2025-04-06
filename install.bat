@echo off
echo Running Create Dump.txt Context Menu Tool installation...
powershell -Command "Start-Process -Verb RunAs -FilePath 'py' -ArgumentList 'scripts/install_contextmenu.py'"
echo Installation completed. Press any key to exit.
pause > nul 
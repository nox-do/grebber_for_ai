@echo off
setlocal enabledelayedexpansion

:: ==========================================================================
:: Skript zum Hinzufügen ODER Entfernen von Kontextmenü-Einträgen
:: für Python-Skripte. Prüft Python-Pfad und existierende Einträge.
:: ==========================================================================
title Dump für AI Context Menu Toggler

:: --------------------------------------------------------------------------
:: Standard-Konfiguration - BITTE PFADE ANPASSEN FALLS NÖTIG
:: --------------------------------------------------------------------------
set "DEFAULT_PYTHON_EXE=C:\Users\Daniel\AppData\Local\Programs\Python\Python313\python.exe"
set "CREATE_DUMP_SCRIPT=C:\git_cursor\grebber_for_ai\scripts\create_dump.py"
set "ADD_IGNORE_SCRIPT=C:\git_cursor\grebber_for_ai\scripts\add_to_ignore.py"

:: Interne Namen für die Registry-Schlüssel (müssen eindeutig und konsistent sein)
set "CREATE_VERB=CreateDump_GrebberAI"
set "IGNORE_VERB=IgnoreForDump_GrebberAI"

:: Angezeigter Text im Kontextmenü
set "CREATE_TEXT=create dump"
set "IGNORE_TEXT=ignore for dump"


:: Aktueller Python-Pfad (wird ggf. vom Benutzer geändert)
set "PYTHON_EXE=%DEFAULT_PYTHON_EXE%"

:: ==========================================================================
:: Administratorrechte prüfen und anfordern
:: ==========================================================================
echo Pruefe auf Administratorrechte...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administratorrechte vorhanden. Fahre fort...
) else (
    echo Administratorrechte benoetigt. Versuche, Rechte anzufordern...
    echo Rechte Maustaste -> 'Als Administrator ausfuehren' falls dies fehlschlaegt.

    :: Versuche, das Skript mit Administratorrechten neu zu starten
    powershell -Command "Start-Process cmd -ArgumentList '/k %~dpnx0' -Verb RunAs"
    exit /b
)
echo.

:: ==========================================================================
:: Python Pfad prüfen und ggf. abfragen (DEBUGGING: PRÜFUNG ÜBERSPRUNGEN)
:: ==========================================================================
:CheckPythonPath
echo Pruefe Python-Pfad: "%PYTHON_EXE%"
echo !!! DEBUG: Python-Existenzpruefung wird uebersprungen !!!
echo !!! DEBUG: Gehe davon aus, dass Python unter "%PYTHON_EXE%" existiert !!!
echo.
REM Folgender Block ist fuer das Debugging auskommentiert:
REM :: Prüfe, ob die Datei existiert mittels 'where'. /Q unterdrückt Ausgabe, wir prüfen errorlevel.
REM where /Q "%PYTHON_EXE%" >nul 2>&1
REM
REM if %errorlevel% equ 0 (
REM     echo Python gefunden.
REM ) else (
REM     echo WARNUNG: Python nicht unter "%PYTHON_EXE%" gefunden!
REM     echo Bitte geben Sie den korrekten vollstaendigen Pfad zur python.exe ein
REM     echo (z.B. C:\Python311\python.exe) oder drücken Sie Enter zum Abbrechen:
REM     set /p "NEW_PYTHON_PATH=> "
REM
REM     if "!NEW_PYTHON_PATH!"=="" (
REM         echo Abbruch durch Benutzer.
REM         goto :ErrorPause
REM     )
REM
REM     :: Setze den neuen Pfad und prüfe erneut
REM     set "PYTHON_EXE=!NEW_PYTHON_PATH!"
REM     echo.
REM     goto :CheckPythonPath
REM )
REM echo Python wird verwendet: "%PYTHON_EXE%"
REM echo.
REM Ende des auskommentierten Blocks

:: Weiter mit dem nächsten Schritt...


:: ==========================================================================
:: Prüfen, ob Einträge bereits existieren
:: ==========================================================================
echo Pruefe auf existierende Kontextmenue-Eintraege...
reg query "HKCR\*\shell\%CREATE_VERB%" >nul 2>&1
if !errorlevel! equ 0 (
    echo Eintraege gefunden. Sie werden jetzt entfernt.
    goto :RemoveEntries
) else (
    echo Keine Eintraege gefunden. Sie werden jetzt hinzugefuegt.
    goto :AddEntries
)
echo.

:: ==========================================================================
:: Funktion: Einträge HINZUFÜGEN
:: ==========================================================================
:AddEntries
echo Fuege Kontextmenue-Eintraege hinzu...
set ACTION_SUCCESS=1

:: --- Create dump ---
echo Fuege %CREATE_TEXT% hinzu...
reg add "HKCR\*\shell\%CREATE_VERB%" /v "" /t REG_SZ /d "%CREATE_TEXT%" /f || set ACTION_SUCCESS=0
reg add "HKCR\*\shell\%CREATE_VERB%\command" /v "" /t REG_SZ /d "\"%PYTHON_EXE%\" \"%CREATE_DUMP_SCRIPT%\" \"%%1\"" /f || set ACTION_SUCCESS=0
reg add "HKCR\Directory\shell\%CREATE_VERB%" /v "" /t REG_SZ /d "%CREATE_TEXT%" /f || set ACTION_SUCCESS=0
reg add "HKCR\Directory\shell\%CREATE_VERB%\command" /v "" /t REG_SZ /d "\"%PYTHON_EXE%\" \"%CREATE_DUMP_SCRIPT%\" \"%%V\"" /f || set ACTION_SUCCESS=0

:: --- Ignore for dump ---
echo Fuege %IGNORE_TEXT% hinzu...
reg add "HKCR\*\shell\%IGNORE_VERB%" /v "" /t REG_SZ /d "%IGNORE_TEXT%" /f || set ACTION_SUCCESS=0
reg add "HKCR\*\shell\%IGNORE_VERB%\command" /v "" /t REG_SZ /d "\"%PYTHON_EXE%\" \"%ADD_IGNORE_SCRIPT%\" \"%%1\"" /f || set ACTION_SUCCESS=0
reg add "HKCR\Directory\shell\%IGNORE_VERB%" /v "" /t REG_SZ /d "%IGNORE_TEXT%" /f || set ACTION_SUCCESS=0
reg add "HKCR\Directory\shell\%IGNORE_VERB%\command" /v "" /t REG_SZ /d "\"%PYTHON_EXE%\" \"%ADD_IGNORE_SCRIPT%\" \"%%V\"" /f || set ACTION_SUCCESS=0

if !ACTION_SUCCESS! equ 1 (
    echo.
    echo Alle Eintraege erfolgreich zur Registry hinzugefuegt.
    goto :ShowSuccessAndExit
) else (
    echo.
    echo FEHLER beim Hinzufuegen eines oder mehrerer Registry-Eintraege!
    goto :ErrorPause
)

:: ==========================================================================
:: Funktion: Einträge ENTFERNEN
:: ==========================================================================
:RemoveEntries
echo Entferne Kontextmenue-Eintraege...
set ACTION_SUCCESS=1

:: --- Create dump ---
echo Entferne %CREATE_TEXT% (%CREATE_VERB%)...
reg delete "HKCR\*\shell\%CREATE_VERB%" /f >nul 2>&1 || set ACTION_SUCCESS=0
reg delete "HKCR\Directory\shell\%CREATE_VERB%" /f >nul 2>&1 || set ACTION_SUCCESS=0

:: --- Ignore for dump ---
echo Entferne %IGNORE_TEXT% (%IGNORE_VERB%)...
reg delete "HKCR\*\shell\%IGNORE_VERB%" /f >nul 2>&1 || set ACTION_SUCCESS=0
reg delete "HKCR\Directory\shell\%IGNORE_VERB%" /f >nul 2>&1 || set ACTION_SUCCESS=0

if !ACTION_SUCCESS! equ 1 (
    echo.
    echo Alle angegebenen Eintraege wurden aus der Registry entfernt (oder waren nicht vorhanden).
    goto :ShowSuccessAndExit
) else (
    echo.
    echo WARNUNG: Fehler beim Entfernen eines oder mehrerer Registry-Eintraege!
    echo (Dies kann passieren, wenn nur Teile der Eintraege vorhanden waren oder ein anderer Fehler auftrat.)
    goto :ErrorPause
)

:: ==========================================================================
:: Erfolgs-Abschluss
:: ==========================================================================
:ShowSuccessAndExit
echo.
echo HINWEIS: Moeglicherweise muessen Sie den Windows Explorer neu starten,
echo          damit die Aenderungen sichtbar werden.
echo          (Task-Manager -> Windows Explorer -> Rechtsklick -> Neu starten)
echo.
echo Druecken Sie eine beliebige Taste zum Beenden...
pause > nul
endlocal
exit /b 0

:: ==========================================================================
:: Fehler-Abschluss
:: ==========================================================================
:ErrorPause
echo.
echo Das Skript wurde mit einem Fehler oder durch den Benutzer beendet.
echo Druecken Sie eine beliebige Taste zum Schliessen...
pause > nul
endlocal
exit /b 1
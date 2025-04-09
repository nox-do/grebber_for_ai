# Grebber for AI

Ein Tool zum Erstellen von Code-Dumps für die Analyse durch KI-Modelle, integriert in das Windows Explorer Kontextmenü. Es sammelt relevante Dateien aus einem Projektverzeichnis, fasst sie in einer `dump.txt`-Datei zusammen und bietet flexible Optionen zum Ignorieren von Dateien und Verzeichnissen.

## Features

*   **Kontextmenü-Integration:** Erstelle Dumps oder füge Dateien/Ordner zu Ignore-Listen hinzu direkt aus dem Windows Explorer.
*   **Intelligente Dateiauswahl:** Sammelt Dateien basierend auf flexiblen Ignore-Regeln.
*   **Ignore-Mechanismen:**
    *   Respektiert automatisch die `.gitignore`-Datei deines Projekts.
    *   Verwendet eine anpassbare Liste von Standard-Ignore-Mustern (z.B. für `node_modules`, `*.log`, `dump.txt`, `.gitignore`).
    *   Ermöglicht das Hinzufügen projekt-spezifischer relativer Pfade zur lokalen Ignore-Liste (`.dump_ignore`).
    *   Unterstützt globale Ignore-Muster und absolute Pfade über die Konfigurationsdatei.
*   **Spracherkennung:** Erkennt die primäre Programmiersprache, um passende Kommentar-Präfixe in Datei-Headern zu verwenden (filtert Dateien *nicht* mehr nach Erweiterung).
*   **Konfigurierbarer Output:** Steuere, ob Datei-Header eingefügt werden und lege eine maximale Dateigröße fest.
*   **Zentralisierte Konfiguration:** Alle Einstellungen und Logs werden sauber im `.dump`-Unterverzeichnis des Projekts verwaltet.

## Installation

1.  **Klonen/Herunterladen:** Lade das Repository herunter oder klone es.
2.  **Abhängigkeiten installieren:** Stelle sicher, dass Python 3.x installiert und im PATH verfügbar ist. Öffne eine Kommandozeile im Projektverzeichnis und installiere die benötigten Pakete:
    ```bash
    pip install -e .
    # Oder manuell, falls setup.py nicht verwendet wird:
    # pip install pywin32==310 toml==0.10.2 gitpython==3.1.31
    ```
3.  **Kontextmenü registrieren:**
    *   Finde die Datei `install_context_menu.bat`.
    *   **Wichtig:** Stelle sicher, dass die Python-Skripte (`create_dump.py`, `add_to_ignore.py`) relativ zur `.bat`-Datei am erwarteten Ort liegen (standardmäßig wird erwartet, dass sie sich im selben Verzeichnis befinden, oft `scripts/` relativ zum Projekt-Root - passe ggf. die Pfade in der `.bat`-Datei an oder verschiebe sie).
    *   Rechtsklicke auf `install_context_menu.bat` und wähle **"Als Administrator ausführen"**.
    *   Folge den Anweisungen im Skript.

## Benutzung

Nach der Installation stehen dir folgende Optionen im Windows Explorer Kontextmenü zur Verfügung:

*   **Rechtsklick auf Ordner-Hintergrund:**
    *   `Create Dump (AI)`: Startet den Dump-Prozess für den aktuellen Ordner. Erstellt/überschreibt `dump.txt` im Ordner-Root.
*   **Rechtsklick auf eine Datei:**
    *   `Add to Local Ignore (AI)`: Fügt den relativen Pfad der Datei zu `.dump/.dump_ignore` hinzu.
    *   `Add to Global Ignore (AI)`: Fügt den absoluten Pfad der Datei zur globalen Ignore-Liste in `.dump/.dump_config` hinzu.
*   **Rechtsklick auf einen Ordner:**
    *   `Add to Local Ignore (AI)`: Fügt den relativen Pfad des Ordners zu `.dump/.dump_ignore` hinzu.
    *   `Add to Global Ignore (AI)`: Fügt den absoluten Pfad des Ordners zur globalen Ignore-Liste in `.dump/.dump_config` hinzu.

## Konfiguration

Das Tool erstellt bei der ersten Verwendung in einem Projekt ein `.dump`-Unterverzeichnis.

*   **`.dump/.dump_config` (TOML-Format):**
    *   Die zentrale Konfigurationsdatei.
    *   `[ignore]`:
        *   `standard_patterns`: **Liste der Standard-Ignore-Muster.** Du kannst diese Liste hier bearbeiten, um die Standard-Ignores anzupassen! Enthält typischerweise Einträge wie `.git`, `node_modules`, `*.log`, `dist/`, `build/`, `dump.txt`, `.gitignore` etc.
        *   `custom_patterns`: Füge hier eigene projektweite Ignore-Muster im `fnmatch`-Stil hinzu (z.B. `**/test_data/*`).
        *   `ignored_paths`: Liste von **absoluten** Pfaden, die global ignoriert werden sollen.
    *   `[output]`:
        *   `include_file_headers`: `true` oder `false`, ob Datei-Header (`// FILE: ...`) eingefügt werden sollen.
        *   `max_file_size`: Maximale Größe einer Datei in Bytes, die in den Dump aufgenommen wird.
    *   Andere Sektionen (`general`, `language`, `languages`, `git`) speichern Metadaten und Erkennungsergebnisse.

*   **`.dump/.dump_ignore` (Textdatei):**
    *   Enthält eine Liste von relativen Pfaden (bezogen auf den Projekt-Root), die lokal ignoriert werden sollen.
    *   Verwende Forward-Slashes (`/`). Ein Eintrag pro Zeile.
    *   Wird typischerweise über das Kontextmenü "Add to Local Ignore (AI)" befüllt.

*   **`.gitignore`:**
    *   Wird automatisch gelesen und berücksichtigt.

## Troubleshooting

*   **Kein Dump erstellt / Unerwartete Dateien ignoriert:**
    *   Stelle sicher, dass die Dateien nicht durch eine Regel in `.gitignore`, `.dump_ignore`, `standard_patterns`, `custom_patterns` oder `ignored_paths` ausgeschlossen werden.
    *   Überprüfe die `.dump/dump_error.log` auf Fehlermeldungen während des Dump-Prozesses.
*   **Kontextmenü-Einträge funktionieren nicht:**
    *   Wurde `install_context_menu.bat` als Administrator ausgeführt?
    *   Ist Python korrekt installiert und im PATH?
    *   Stimmen die Pfade zu den Python-Skripten (`create_dump.py`, `add_to_ignore.py`) in der `.bat`-Datei?
    *   Existieren die Python-Skripte an den erwarteten Orten?
*   **Fehlermeldungen beim Ausführen:**
    *   Überprüfe `.dump/dump_error.log` für Details.

## Abhängigkeiten

*   Python 3.x
*   pywin32==310
*   toml==0.10.2
*   GitPython==3.1.31
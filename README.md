# Create Dump.txt Context Menu Tool

A Windows context menu tool that creates a consolidated text file (`dump.txt`) containing all relevant code files from a project directory. The tool automatically detects the programming language and applies appropriate filtering and formatting.

## Features

- Automatic language detection (Java, JavaScript, TypeScript, Python)
- Smart file filtering (ignores common build/dependency directories)
- Custom ignore list support
- Language-specific comment formatting
- Windows context menu integration

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the installation script by double-clicking `install.bat` or running it from an administrator command prompt:
   ```
   install.bat
   ```

   Note: The installation requires administrator privileges to modify the Windows Registry.

## Usage

### Creating a Dump

1. Right-click on any project directory in Windows Explorer
2. Select "Create dump.txt" from the context menu
3. A `dump.txt` file will be created in the selected directory containing all relevant code files

### Adding Files to Ignore List

1. Right-click on any file or directory in Windows Explorer
2. Select "Add to ignore for dump" from the context menu
3. The file/directory will be added to the ignore list and won't be included in future dumps

## Uninstallation

To remove the context menu entries, double-click `uninstall.bat` or run it from an administrator command prompt:
```
uninstall.bat
```

Note: The uninstallation requires administrator privileges to modify the Windows Registry.

## Project Structure

```
create_dump_contextmenu/
├── scripts/
│   ├── install_contextmenu.py
│   ├── uninstall_contextmenu.py
│   ├── add_to_ignore.py
│   └── create_dump.py
│
├── detectors/
│   ├── language_detector.py
│   ├── languages.py
│   └── filter.py
│
├── utils/
│   ├── file_utils.py
│   └── comment_utils.py
│
├── data/
│   └── ignore_list.txt
│
├── install.bat
├── uninstall.bat
├── requirements.txt
└── README.md
```

## Supported Languages

- Java (.java, pom.xml, .gradle)
- JavaScript (.js, .jsx, package.json)
- TypeScript (.ts, .tsx, tsconfig.json)
- Python (.py, requirements.txt, pyproject.toml)

## Default Ignored Patterns

The following patterns are ignored by default:
- `.git`
- `.idea`
- `.venv`
- `__pycache__`
- `node_modules`
- `*.lock`
- `*.log`
- `dist`
- `build` 
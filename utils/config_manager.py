# --- START OF FILE utils/config_manager.py ---
import os
import toml
import git # Make sure gitpython is installed if using this actively
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
import fnmatch
from .ignore_manager import IgnoreManager
from .error_logger import log_error

# --- Definition der Standard-Ignore-Patterns als Konstante ---
DEFAULT_STANDARD_IGNORE_PATTERNS: Tuple[str, ...] = (
    # Version Control System
    '.git', '.svn', '.hg',
    # IDEs and Editors
    '.idea', '.vscode',
    '*.swp', '*.swo', '*.swn',
    # Python specific
    '*.pyc', '*.pyo', '*.pyd',
    '__pycache__', '.pytest_cache', '.mypy_cache', '.tox', '.nox',
    '.venv', 'venv', 'env', '.env',
    '*.egg-info',
    # Node specific
    'node_modules', 'bower_components',
    'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*',
    # Build output
    'dist', 'build', 'target', 'out', 'bin', 'obj',
    # Logs and temporary files
    '*.log', '*.tmp',
    # Lock files
    '*.lock', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'composer.lock',
    # OS specific
    '.DS_Store', 'Thumbs.db',
    # Tool specific (Grebber for AI)
    '.dump',         # Ignore the tool's own config/log directory
    '.gitignore',    # Usually not needed in the dump itself
    'dump.txt'       # Ignore the tool's output file
)
# --------------------------------------------------------------

class ConfigManager:
    """
    Manages the .dump_config file (inside .dump directory) and coordinates ignore logic.
    """
    CONFIG_FILENAME = ".dump_config"
    DUMP_SUBDIR = ".dump" # Define the subdirectory name

    def __init__(self, project_dir: str):
        """Initialize the config manager for a project directory."""
        self.project_dir = Path(project_dir).resolve()
        self.dump_dir_path = self.project_dir / self.DUMP_SUBDIR
        self.config_path = self.dump_dir_path / self.CONFIG_FILENAME
        self.config = self._load_or_create_config()

        # Initialize ignore managers
        self.gitignore_patterns = self._load_gitignore_patterns()
        self.local_ignore = IgnoreManager(str(self.project_dir)) # Pass project dir

    def _ensure_dump_dir_exists(self):
        """Creates the .dump directory if it doesn't exist."""
        try:
            self.dump_dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log_error(str(self.project_dir), f"Warning: Failed to create dump directory {self.dump_dir_path}: {e}")

    def _load_or_create_config(self) -> Dict:
        """Load existing config from .dump/ or create a new one."""
        self._ensure_dump_dir_exists()
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = toml.load(f)
                    # Ensure important sections exist after loading
                    if 'ignore' not in loaded_config: loaded_config['ignore'] = {}
                    if 'standard_patterns' not in loaded_config['ignore']: loaded_config['ignore']['standard_patterns'] = []
                    if 'custom_patterns' not in loaded_config['ignore']: loaded_config['ignore']['custom_patterns'] = []
                    if 'ignored_paths' not in loaded_config['ignore']: loaded_config['ignore']['ignored_paths'] = []
                    if 'output' not in loaded_config: loaded_config['output'] = {}
                    if 'language' not in loaded_config: loaded_config['language'] = {} # Ensure language section exists
                    return loaded_config
            except Exception as e:
                 log_error(str(self.project_dir), f"Failed to load config file {self.config_path}: {e}. Creating default config.")
                 return self._create_default_config(save=True)
        return self._create_default_config(save=True)

    def _create_default_config(self, save: bool = False) -> Dict:
        """Create a new default configuration dictionary."""
        config = {
            'general': {
                'last_dump_time': datetime.now().isoformat(),
                'version': '1.0.0'
            },
            'git': self._detect_git_info(),
            'language': {
                'primary_language': None,
                'detected_languages': []
            },
            'ignore': {
                'standard_patterns': list(DEFAULT_STANDARD_IGNORE_PATTERNS),
                'custom_patterns': [],
                'ignored_paths': []
            },
            'languages': {
                 'python': { 'extensions': ['.py'], 'marker_files': ['requirements.txt', 'pyproject.toml'], 'comment_prefix': '#' },
                 'javascript': { 'extensions': ['.js', '.jsx', '.mjs', '.cjs'], 'marker_files': ['package.json'], 'comment_prefix': '//' },
                 'typescript': { 'extensions': ['.ts', '.tsx', '.mts', '.cts'], 'marker_files': ['tsconfig.json'], 'comment_prefix': '//' },
                 'java': { 'extensions': ['.java'], 'marker_files': ['pom.xml', 'build.gradle', 'settings.gradle'], 'comment_prefix': '//' },
            },
            'output': {
                'format': 'text',
                'include_line_numbers': False,
                'include_file_headers': True,
                'max_file_size': 1024 * 1024
            }
        }
        if save:
            try:
                self._ensure_dump_dir_exists()
                self.save_config(config) # Pass the dict to save here
            except Exception as e:
                 pass # save_config logs errors
        return config

    def _detect_git_info(self) -> Dict:
        """Detect Git repository information."""
        try:
            git_dir = self.project_dir / '.git'
            if git_dir.exists() and git_dir.is_dir():
                return { 'git_dir': '.git', 'is_git_repo': True }
            return { 'git_dir': None, 'is_git_repo': False }
        except git.InvalidGitRepositoryError:
             return { 'git_dir': None, 'is_git_repo': False }
        except Exception as e:
            log_error(str(self.project_dir), f"Error detecting git info: {e}")
            return { 'git_dir': None, 'is_git_repo': False }

    def _load_gitignore_patterns(self) -> List[str]:
        """Load patterns from .gitignore file if it exists in the project root."""
        gitignore_path = self.project_dir / '.gitignore'
        patterns = []
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                log_error(str(self.project_dir), f"Error reading .gitignore file {gitignore_path}: {e}")
        return patterns

    def save_config(self, config_to_save: Optional[Dict] = None) -> None: # Renamed internal var
        """Save the provided configuration dictionary (or instance config) to .dump/.dump_config file."""
        if config_to_save is None:
            config_to_save = self.config # Save the current instance config if none provided

        self._ensure_dump_dir_exists()
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write("# Configuration for Grebber for AI\n")
                f.write("# You can modify settings here, especially ignore patterns.\n\n")
                toml.dump(config_to_save, f)
            # If we just saved a config passed as argument, update instance config?
            # Yes, makes sense if _create_default_config passes 'config' to save it.
            if config_to_save is not self.config:
                 self.config = config_to_save
        except Exception as e:
             log_error(str(self.project_dir), f"Failed to save config file {self.config_path}: {e}")

    def update_last_dump_time(self) -> None:
        """Update the last dump time in the config."""
        # Ensure general section exists
        if 'general' not in self.config: self.config['general'] = {}
        self.config['general']['last_dump_time'] = datetime.now().isoformat()
        self.save_config() # Saves self.config

    # --- !!! METHOD RE-ADDED HERE !!! ---
    def update_language_info(self, primary_language: Optional[str], detected_languages: List[Dict[str, float]]) -> None:
        """Update language detection information in the config."""
        # Ensure language section exists
        if 'language' not in self.config:
            self.config['language'] = {}
        self.config['language']['primary_language'] = primary_language
        self.config['language']['detected_languages'] = detected_languages
        self.save_config() # Saves self.config
    # --- END OF RE-ADDED METHOD ---

    def _get_absolute_path(self, path: str) -> Path:
        """Converts a path string to a resolved absolute Path object."""
        path_obj = Path(path)
        if not path_obj.is_absolute():
            return (self.project_dir / path_obj).resolve()
        return path_obj.resolve()

    def add_to_ignore(self, path: str, globally: bool = False) -> None:
        """
        Add a path to the appropriate ignore list.
        Args:
            path: Path to ignore. If globally=True, absolute path. If globally=False, relative to project root.
            globally: True adds absolute path to global config, False adds relative path to local .dump_ignore.
        """
        if globally:
            abs_path_obj = self._get_absolute_path(path)
            abs_path_str = str(abs_path_obj)
            # Ensure ignore section and ignored_paths list exist
            if 'ignore' not in self.config: self.config['ignore'] = {}
            if 'ignored_paths' not in self.config['ignore']: self.config['ignore']['ignored_paths'] = []
            elif not isinstance(self.config['ignore']['ignored_paths'], list):
                 log_error(str(self.project_dir), f"Config Error: ignore.ignored_paths is not a list. Resetting.")
                 self.config['ignore']['ignored_paths'] = []

            if abs_path_str not in self.config['ignore']['ignored_paths']:
                self.config['ignore']['ignored_paths'].append(abs_path_str)
                self.save_config() # Save the updated self.config
        else:
            # Path is expected to be relative to project root already
            self.local_ignore.add_path(path) # Delegate directly

    def add_global_pattern(self, pattern: str) -> None:
        """Add a global ignore pattern (fnmatch style) to custom_patterns."""
        # Ensure ignore section and custom_patterns list exist
        if 'ignore' not in self.config: self.config['ignore'] = {}
        if 'custom_patterns' not in self.config['ignore']: self.config['ignore']['custom_patterns'] = []
        elif not isinstance(self.config['ignore']['custom_patterns'], list):
             log_error(str(self.project_dir), f"Config Error: ignore.custom_patterns is not a list. Resetting.")
             self.config['ignore']['custom_patterns'] = []

        if pattern not in self.config['ignore']['custom_patterns']:
            self.config['ignore']['custom_patterns'].append(pattern)
            self.save_config() # Save the updated self.config

    def clean_ignore_list(self) -> None:
        """Clean the global 'ignored_paths' list by removing non-existent absolute paths."""
        # Ensure ignore section and ignored_paths list exist
        if 'ignore' not in self.config: self.config['ignore'] = {}
        if 'ignored_paths' in self.config['ignore'] and isinstance(self.config['ignore']['ignored_paths'], list):
            original_paths = self.config['ignore']['ignored_paths']
            existing_paths = []
            changed = False
            for path_str in original_paths:
                try:
                    if Path(path_str).exists():
                        existing_paths.append(path_str)
                    else:
                        changed = True
                except Exception as e:
                    log_error(str(self.project_dir), f"Error checking existence for ignored path '{path_str}': {e}")
                    existing_paths.append(path_str)

            if changed:
                self.config['ignore']['ignored_paths'] = existing_paths
                self.save_config() # Save the updated self.config

    def get_ignore_patterns(self) -> Set[str]:
        """Get all ignore patterns (standard from config + custom from config + gitignore)."""
        standard = set(self.config.get('ignore', {}).get('standard_patterns', []))
        custom = set(self.config.get('ignore', {}).get('custom_patterns', []))
        gitignore = set(self.gitignore_patterns) # Loaded during init
        return standard.union(custom).union(gitignore)

    def get_ignored_paths(self) -> Set[str]:
        """Get all globally ignored absolute paths from config."""
        return set(self.config.get('ignore', {}).get('ignored_paths', []))

    def _matches_pattern(self, path_to_check: Path, relative_path_str: str) -> bool:
        """Checks if the path matches any ignore pattern (standard, custom, gitignore)."""
        file_name = path_to_check.name
        patterns = self.get_ignore_patterns()
        relative_path_str_norm = relative_path_str.replace('\\', '/')

        for pattern in patterns:
            clean_pattern = pattern.strip().replace('\\', '/')
            if not clean_pattern: continue # Skip empty patterns

            if clean_pattern.endswith('/'):
                pattern_base = clean_pattern.rstrip('/')
                if path_to_check.is_dir() and (relative_path_str_norm == pattern_base or relative_path_str_norm.startswith(pattern_base + '/')):
                     return True
                # Check if item is within a dir matching the pattern (more general)
                if relative_path_str_norm.startswith(pattern_base + '/'):
                     return True

            elif clean_pattern.startswith('/'):
                 pattern_base = clean_pattern.lstrip('/')
                 # Match only from the root
                 if fnmatch.fnmatch(relative_path_str_norm, pattern_base):
                      return True

            else: # General pattern matching (applies anywhere)
                if fnmatch.fnmatch(relative_path_str_norm, clean_pattern) or fnmatch.fnmatch(file_name, clean_pattern):
                    return True
        return False


    def is_ignored(self, path: str) -> bool:
        """Check if a given path should be ignored based on all rules."""
        try:
            abs_path_obj = self._get_absolute_path(path)
            abs_path_str = str(abs_path_obj)

            # 1. Check global absolute ignored paths
            if abs_path_str in self.get_ignored_paths():
                return True

            # Calculate relative path for local and pattern checks
            rel_path_str = abs_path_obj.name # Default to filename if outside project
            is_within_project = False
            try:
                rel_path_obj = abs_path_obj.relative_to(self.project_dir)
                rel_path_str = str(rel_path_obj).replace('\\', '/').strip('/')
                is_within_project = True
            except ValueError:
                # Path is outside project dir. Local rules don't apply directly.
                pass # Use filename for pattern check below

            # 2. Check local .dump_ignore (only if path is inside project)
            if is_within_project and self.local_ignore.is_ignored(rel_path_str):
                return True

            # 3. Check all patterns (Standard, Custom, .gitignore)
            # Use the relative path string (or filename if outside project)
            if self._matches_pattern(abs_path_obj, rel_path_str):
                 return True

        except OSError as e:
            log_error(str(self.project_dir), f"Cannot process path due to OS error: '{path}'. Error: {e}")
            return True # Treat inaccessible/invalid paths as ignored
        except Exception as e:
            log_error(str(self.project_dir), f"Unexpected error checking ignore status for path '{path}': {e}")
            return True # Treat errors conservatively as ignored

        return False # Not ignored by any rule

    def get_language_settings(self, language_key: str) -> Optional[Dict]:
        """Get settings for a specific language from config."""
        # Ensure languages section exists
        if 'languages' not in self.config: self.config['languages'] = {}
        return self.config.get('languages', {}).get(language_key)

    def get_output_settings(self) -> Dict:
        """Get output settings, ensuring correct types and providing defaults."""
        defaults = {
            'format': 'text',
            'include_line_numbers': False,
            'include_file_headers': True,
            'max_file_size': 1024 * 1024
        }
        output_cfg = self.config.get('output', {}) # Already ensured output exists minimally
        defaults.update(output_cfg)

        try:
             defaults['max_file_size'] = int(defaults['max_file_size'])
        except (ValueError, TypeError):
             log_error(str(self.project_dir), f"Invalid 'max_file_size' in config ({output_cfg.get('max_file_size')}). Using 1MB default.")
             defaults['max_file_size'] = 1024 * 1024

        defaults['include_line_numbers'] = str(defaults.get('include_line_numbers', False)).lower() == 'true'
        defaults['include_file_headers'] = str(defaults.get('include_file_headers', True)).lower() == 'true'

        return defaults

# --- END OF FILE utils/config_manager.py ---
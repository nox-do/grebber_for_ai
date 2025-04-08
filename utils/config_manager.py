import os
import toml
import git
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
import fnmatch
from .ignore_manager import IgnoreManager

class ConfigManager:
    """Manages the .dump_config file for global configuration."""
    
    CONFIG_FILENAME = ".dump_config"
    
    def __init__(self, project_dir: str):
        """Initialize the config manager for a project directory."""
        self.project_dir = Path(project_dir).resolve()
        self.config_path = self.project_dir / self.CONFIG_FILENAME
        self.config = self._load_or_create_config()
        
        # Initialize ignore managers
        self.gitignore_patterns = self._load_gitignore_patterns()
        self.local_ignore = IgnoreManager(project_dir)
        
    def _load_or_create_config(self) -> Dict:
        """Load existing config or create a new one."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create a new default configuration."""
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
                'standard_patterns': [
                    '.git', '.idea', '.venv', '__pycache__',
                    'node_modules', '*.lock', '*.log', 'dist', 'build'
                ],
                'custom_patterns': [],
                'ignored_paths': []
            },
            'languages': {
                'python': {
                    'extensions': ['.py'],
                    'marker_files': ['requirements.txt', 'pyproject.toml'],
                    'comment_prefix': '#'
                },
                'javascript': {
                    'extensions': ['.js', '.jsx'],
                    'marker_files': ['package.json'],
                    'comment_prefix': '//'
                },
                'typescript': {
                    'extensions': ['.ts', '.tsx'],
                    'marker_files': ['tsconfig.json'],
                    'comment_prefix': '//'
                },
                'java': {
                    'extensions': ['.java'],
                    'marker_files': ['pom.xml', 'build.gradle'],
                    'comment_prefix': '//'
                }
            },
            'output': {
                'format': 'text',
                'include_line_numbers': True,
                'include_file_headers': True,
                'max_file_size': 1024 * 1024  # 1MB
            }
        }
        
        # Save the new config
        self.save_config(config)
        return config
    
    def _detect_git_info(self) -> Dict:
        """Detect Git repository information."""
        try:
            # Try to find .git directory in the project directory
            git_dir = self.project_dir / '.git'
            if git_dir.exists() and git_dir.is_dir():
                return {
                    'git_dir': '.git',
                    'is_git_repo': True
                }
            return {
                'git_dir': None,
                'is_git_repo': False
            }
        except Exception:
            return {
                'git_dir': None,
                'is_git_repo': False
            }
    
    def _load_gitignore_patterns(self) -> List[str]:
        """Load patterns from .gitignore file if it exists."""
        gitignore_path = self.project_dir / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                # Parse .gitignore file and extract patterns
                patterns = []
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.append(line)
                return patterns
        return []
    
    def save_config(self, config: Optional[Dict] = None) -> None:
        """Save the configuration to file."""
        if config is None:
            config = self.config
            
        with open(self.config_path, 'w', encoding='utf-8') as f:
            toml.dump(config, f)
    
    def update_last_dump_time(self) -> None:
        """Update the last dump time in the config."""
        self.config['general']['last_dump_time'] = datetime.now().isoformat()
        self.save_config()
    
    def _normalize_path(self, path: str) -> str:
        """Normalize a path to a consistent format.
        
        This ensures that paths are stored in a consistent format, making it easier
        to detect duplicates.
        """
        # Convert to Path object
        path_obj = Path(path)
        
        # If path is not absolute, make it absolute relative to the project directory
        if not path_obj.is_absolute():
            path_obj = (self.project_dir / path_obj).resolve()
        else:
            path_obj = path_obj.resolve()
            
        # Always store absolute paths for global config
        return str(path_obj)
    
    def add_to_ignore(self, path: str, globally: bool = False) -> None:
        """Add a path to the ignore list.
        
        Args:
            path: Path to ignore
            globally: If True, add to global config, otherwise add to local .dump_ignore
        """
        if globally:
            normalized_path = self._normalize_path(path)
            if normalized_path not in self.config['ignore']['ignored_paths']:
                self.config['ignore']['ignored_paths'].append(normalized_path)
                self.save_config()
        else:
            self.local_ignore.add_path(path)
    
    def add_global_pattern(self, pattern: str) -> None:
        """Add a global ignore pattern."""
        if pattern not in self.config['ignore']['custom_patterns']:
            self.config['ignore']['custom_patterns'].append(pattern)
            self.save_config()
    
    def clean_ignore_list(self) -> None:
        """Clean the ignore list by removing non-existent paths."""
        existing_paths = []
        for path in self.config['ignore']['ignored_paths']:
            if os.path.exists(path):
                existing_paths.append(path)
        
        self.config['ignore']['ignored_paths'] = existing_paths
        self.save_config()
    
    def update_language_info(self, primary_language: str, detected_languages: List[Dict[str, float]]) -> None:
        """Update language detection information."""
        self.config['language']['primary_language'] = primary_language
        self.config['language']['detected_languages'] = detected_languages
        self.save_config()
    
    def get_ignore_patterns(self) -> Set[str]:
        """Get all ignore patterns (standard + custom + gitignore)."""
        all_patterns = set(self.config['ignore']['standard_patterns'] + 
                         self.config['ignore']['custom_patterns'] + 
                         self.gitignore_patterns)
        return all_patterns
    
    def get_ignored_paths(self) -> Set[str]:
        """Get all ignored absolute paths."""
        return set(self.config['ignore']['ignored_paths'])
    
    def is_ignored(self, path: str) -> bool:
        """Check if a path should be ignored."""
        normalized_path = self._normalize_path(path)
        
        # Check global ignored paths
        if normalized_path in self.get_ignored_paths():
            return True
            
        # Check local .dump_ignore
        if self.local_ignore.is_ignored(path):
            return True
            
        # Check patterns
        for pattern in self.get_ignore_patterns():
            if fnmatch.fnmatch(normalized_path, pattern):
                return True
                
        return False
    
    def get_language_settings(self, language_key: str) -> Optional[Dict]:
        """Get settings for a specific language."""
        return self.config['languages'].get(language_key)
    
    def get_output_settings(self) -> Dict:
        """Get output settings."""
        return self.config['output'] 
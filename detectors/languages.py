from dataclasses import dataclass
from typing import List, Set, Dict

@dataclass
class Language:
    name: str
    extensions: Set[str]
    marker_files: Set[str]
    comment_prefix: str

# Define supported languages
LANGUAGES: Dict[str, Language] = {
    'java': Language(
        name='Java',
        extensions={'.java'},
        marker_files={'pom.xml', '.gradle'},
        comment_prefix='//'
    ),
    'javascript': Language(
        name='JavaScript',
        extensions={'.js', '.jsx'},
        marker_files={'package.json'},
        comment_prefix='//'
    ),
    'typescript': Language(
        name='TypeScript',
        extensions={'.ts', '.tsx'},
        marker_files={'tsconfig.json'},
        comment_prefix='//'
    ),
    'python': Language(
        name='Python',
        extensions={'.py'},
        marker_files={'requirements.txt', 'pyproject.toml'},
        comment_prefix='#'
    )
}

# Standard ignore patterns
IGNORE_PATTERNS = {
    '.git',
    '.idea',
    '.venv',
    '__pycache__',
    'node_modules',
    '*.lock',
    '*.log',
    'dist',
    'build'
} 
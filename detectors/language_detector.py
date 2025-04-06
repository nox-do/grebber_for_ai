import os
from typing import Optional, Set
from .languages import LANGUAGES

def detect_language(directory: str) -> Optional[str]:
    """
    Detect the dominant programming language in the given directory.
    Returns the language key or None if no language could be detected.
    """
    # Count occurrences of marker files and extensions
    language_scores = {lang: 0 for lang in LANGUAGES.keys()}
    
    for root, _, files in os.walk(directory):
        for file in files:
            # Check marker files
            for lang_key, lang_info in LANGUAGES.items():
                if file in lang_info.marker_files:
                    language_scores[lang_key] += 2  # Marker files count double
                
                # Check file extensions
                if any(file.endswith(ext) for ext in lang_info.extensions):
                    language_scores[lang_key] += 1
    
    # Find language with highest score
    max_score = max(language_scores.values())
    if max_score == 0:
        return None
        
    # Return the first language with the maximum score
    return next(lang for lang, score in language_scores.items() if score == max_score) 
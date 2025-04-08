import os
from typing import Optional, Set, Tuple, List, Dict
from .languages import LANGUAGES

def detect_language(directory: str) -> Tuple[Optional[str], List[Dict[str, float]]]:
    """
    Detect the dominant programming language in the given directory.
    Returns a tuple of (language_key, detected_languages_with_confidence).
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
    
    # Calculate total score
    total_score = sum(language_scores.values())
    if total_score == 0:
        return None, []
    
    # Calculate confidence scores
    detected_languages = []
    for lang_key, score in language_scores.items():
        if score > 0:
            confidence = score / total_score
            detected_languages.append({
                "name": lang_key,
                "confidence": round(confidence, 2)
            })
    
    # Sort by confidence (highest first)
    detected_languages.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Find language with highest score
    max_score = max(language_scores.values())
    if max_score == 0:
        return None, []
        
    # Return the first language with the maximum score and all detected languages
    primary_language = next(lang for lang, score in language_scores.items() if score == max_score)
    return primary_language, detected_languages 
from typing import Optional
from detectors.languages import LANGUAGES

def get_file_comment(file_path: str, language_key: str) -> str:
    """
    Get the comment line for a file based on the detected language.
    """
    if language_key not in LANGUAGES:
        return ""
        
    lang_info = LANGUAGES[language_key]
    return f"{lang_info.comment_prefix} {file_path}"

def ensure_file_comment(content: str, comment: str) -> str:
    """
    Ensure the file content starts with the correct comment.
    If it doesn't, add it as the first line.
    """
    lines = content.splitlines()
    if not lines:
        return comment
        
    first_line = lines[0].strip()
    if first_line.startswith(comment.split()[0]):  # Check if comment prefix exists
        return content
        
    return f"{comment}\n{content}" 
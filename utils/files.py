import os
import re


def ensure_directory_exists(directory):
    """Creates a folder if it doesn't exist"""

    os.makedirs(directory, exist_ok=True)


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """Converts a string into a valid filename by removing or replacing invalid characters"""

    invalid_chars_pattern = re.compile(
        r'[<>:"/\\|?*\s\x00-\x1F\x7F\x80-\x9F\u2000-\u200A\u2028\u2029\u202A-\u202E\u2060\uFEFF]'
    )
    filename = invalid_chars_pattern.sub(replacement, filename)  # Remove special characters
    filename = filename.strip().rstrip(".")  # Remove leading/trailing spaces and dots

    if not filename:  # If the filename is empty after sanitization, assign a default name
        filename = "default_filename"

    return filename


def rename_file(old_filename, new_filename):
    """Renames a file if it exists"""

    if not os.path.exists(old_filename):
        print(f"File not found: {old_filename}")
        return

    base, ext = os.path.splitext(new_filename)
    counter = 1
    new_filepath = new_filename

    while os.path.exists(new_filepath):
        new_filepath = f"{base}_{counter}{ext}"
        counter += 1

    os.rename(old_filename, new_filepath)

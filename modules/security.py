"""
Security functions for the UOM Results Ranking Tool.
Implements file validation, sanitization, and LFI prevention.
"""

import os
import re
import uuid
import glob
from datetime import datetime, timedelta
from typing import List, Tuple
import pandas as pd

from .config import (
    MAX_FILE_SIZE_BYTES, 
    MAX_FILE_SIZE_MB,
    EXPORTS_DIR, 
    ALLOWED_EXPORT_EXTENSIONS
)


def validate_file_size(uploaded_file) -> Tuple[bool, str]:
    """Validate file size is within limits."""
    if uploaded_file is None:
        return False, "No file uploaded"
    
    file_size = uploaded_file.size
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds limit of {MAX_FILE_SIZE_MB} MB"
    
    return True, "File size OK"


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Tuple[bool, str]:
    """Validate file has an allowed extension."""
    if not filename:
        return False, "No filename provided"
    
    ext = os.path.splitext(filename.lower())[1]
    if ext not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
    
    return True, "File type OK"


def sanitize_string(s: str) -> str:
    """Sanitize string to prevent injection attacks."""
    if not isinstance(s, str):
        return str(s)
    # Remove any potentially dangerous characters
    return re.sub(r'[<>{}|\\^~\[\]`]', '', s)


def cleanup_old_exports(max_age_hours: int = 1):
    """
    Clean up export files older than max_age_hours.
    Security: Only removes files from EXPORTS_DIR with allowed extensions.
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for filepath in glob.glob(os.path.join(EXPORTS_DIR, "*")):
            # Security: Verify file is within exports directory (prevent path traversal)
            real_path = os.path.realpath(filepath)
            if not real_path.startswith(os.path.realpath(EXPORTS_DIR)):
                continue
            
            # Only delete allowed file types
            ext = os.path.splitext(filepath)[1].lower()
            if ext not in ALLOWED_EXPORT_EXTENSIONS:
                continue
            
            # Skip symlinks
            if os.path.islink(filepath):
                continue
            
            # Check file age
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_mtime < cutoff_time:
                os.remove(filepath)
    except Exception:
        pass  # Silently fail cleanup - not critical


def save_export_file(df: pd.DataFrame, file_format: str) -> Tuple[str, str]:
    """
    Securely save a dataframe to the exports directory.
    
    Security measures:
    - UUID-based filename (no user input)
    - Fixed directory (EXPORTS_DIR)
    - Whitelist file extensions
    - Path validation
    
    Returns:
        Tuple of (filename, full_path)
    """
    # Security: Only allow whitelisted formats
    allowed_formats = {'csv': '.csv', 'xlsx': '.xlsx'}
    if file_format not in allowed_formats:
        raise ValueError(f"Invalid format. Allowed: {list(allowed_formats.keys())}")
    
    # Generate secure filename with UUID (no user input)
    file_uuid = uuid.uuid4().hex[:16]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rankings_{timestamp}_{file_uuid}{allowed_formats[file_format]}"
    
    # Security: Build path safely - no user input in path
    filepath = os.path.join(EXPORTS_DIR, filename)
    
    # Security: Validate the path is within EXPORTS_DIR (prevent path traversal)
    real_exports_dir = os.path.realpath(EXPORTS_DIR)
    real_filepath = os.path.realpath(filepath)
    if not real_filepath.startswith(real_exports_dir):
        raise ValueError("Security error: Invalid file path")
    
    # Skip symlinks
    if os.path.islink(filepath):
        raise ValueError("Security error: Invalid file path")   
    
    # Save the file
    if file_format == 'csv':
        df.to_csv(filepath, index=False)
    elif file_format == 'xlsx':
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Rankings')
    
    return filename, filepath


def get_download_link(filename: str) -> str:
    """
    Get a secure download path for an exported file.
    
    Security: Validates filename is within EXPORTS_DIR and has allowed extension.
    """
    # Security: Whitelist allowed extensions
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXPORT_EXTENSIONS:
        raise ValueError("Invalid file extension")
    
    # Security: Sanitize filename (remove any path components)
    safe_filename = os.path.basename(filename)
    
    # Security: Build path and validate it's within EXPORTS_DIR
    filepath = os.path.join(EXPORTS_DIR, safe_filename)
    real_exports_dir = os.path.realpath(EXPORTS_DIR)
    real_filepath = os.path.realpath(filepath)
    
    if not real_filepath.startswith(real_exports_dir):
        raise ValueError("Security error: Path traversal detected")
    
    if not os.path.exists(filepath):
        raise ValueError("File not found")
    
    return filepath

"""
Configuration constants for the UOM Results Ranking Tool.
"""

import os

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_DEPT_EXTENSIONS = ['.csv', '.xlsx', '.xls']
ALLOWED_PDF_EXTENSION = '.pdf'
ALLOWED_EXPORT_EXTENSIONS = {'.csv', '.xlsx'}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

GRADE_POINTS = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D': 1.0, 'I-we': 0.0, 'I-ca': 0.0, 'F': 0.0, 'AB': 0.0
}

EXPORT_CLEANUP_HOURS = 0.5

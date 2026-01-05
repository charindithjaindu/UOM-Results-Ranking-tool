# UOM Results Ranking Tool

A user-friendly Streamlit web application for processing exam results and generating student rankings.

## Features

- 📁 **Department File Upload** - Load student lists from CSV or Excel
- 📄 **PDF Grade Extraction** - Automatically extract grades from result PDFs
- ⚖️ **Weighted SGPA Calculation** - Calculate SGPA with customizable module weights
- 🏆 **Ranking Generation** - Generate rankings with downloadable results
- 🔒 **Security** - File size limits, validation, LFI prevention, symlink protection

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. Follow the steps in the UI:
   - Upload department file (CSV/Excel with Index column)
   - Add result PDFs one by one
   - Set module weights (credits)
   - Generate rankings and download results

## Project Structure

```
UOMResults/
├── app.py                 # Main Streamlit application
├── modules/               # Modular components
│   ├── __init__.py       # Package initialization
│   ├── config.py         # Configuration constants
│   ├── security.py       # Security functions & file validation
│   ├── pdf_processor.py  # PDF extraction logic
│   ├── data_processor.py # Data loading & SGPA calculation
│   └── ui_components.py  # UI rendering functions
├── exports/              # Temporary export files (auto-cleaned)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Security Features

- ✅ File size limit (10MB)
- ✅ File type whitelist validation
- ✅ Path traversal prevention
- ✅ Symlink attack prevention
- ✅ UUID-based filenames (no user input in paths)
- ✅ Input sanitization
- ✅ Auto cleanup of old exports (1 hour)

## Module Descriptions

### `config.py`
Constants and configuration including:
- File size limits
- Allowed extensions
- Grade point mappings
- Export settings

### `security.py`
Security functions:
- File validation (size, type, path)
- Secure file export with LFI prevention
- Old file cleanup
- String sanitization

### `pdf_processor.py`
PDF processing:
- Text extraction (PyPDF2 + pdfplumber fallback)
- Module code/name detection
- Grade parsing with regex

### `data_processor.py`
Data operations:
- Department file loading (CSV/Excel)
- Grade merging
- SGPA calculation with weights
- Ranking generation

### `ui_components.py`
Streamlit UI:
- Header with dark mode support
- How-it-works guide
- Module banners
- Weight input forms
- Footer

## Development

The code is modularized for maintainability:
- Each module has a single responsibility
- Relative imports within the modules package
- Type hints for better IDE support
- Comprehensive docstrings

## Requirements

- Python 3.7+
- streamlit >= 1.28.0
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- PyPDF2 >= 3.0.0
- pdfplumber >= 0.10.0


Made with ❤️ for UOM Students

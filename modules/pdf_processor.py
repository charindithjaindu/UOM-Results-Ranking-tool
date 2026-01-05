"""
PDF processing functions for the UOM Results Ranking Tool.
Handles extraction of grades from result PDFs.
"""

import io
import re
from typing import List, Dict, Tuple, Optional
import pandas as pd
import streamlit as st

from .security import sanitize_string


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyPDF2."""
    try:
        import PyPDF2
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.warning(f"PyPDF2 extraction failed, trying pdfplumber: {str(e)[:50]}")
        # Try pdfplumber as fallback
        try:
            import pdfplumber
            pdf_file = io.BytesIO(pdf_bytes)
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except ImportError:
            st.error("Please install pdfplumber: pip install pdfplumber")
            return ""
        except Exception as e2:
            st.error(f"PDF extraction failed: {e2}")
            return ""


def extract_module_info(text: str) -> Tuple[str, str]:
    """Extract module code and name from text."""
    # Pattern like "MA1014 - Mathematics" or "CS2043 - Operating Systems"
    module_pattern = r'([A-Z]{2}\d{4})\s*-\s*([A-Za-z\s]+?)(?=\n|Intake|$)'
    match = re.search(module_pattern, text)
    
    if match:
        module_code = match.group(1).strip()
        module_name = match.group(2).strip()
        return module_code, module_name
    
    # Fallback - just get module code
    code_pattern = r'[A-Z]{2}\d{4}'
    match = re.search(code_pattern, text)
    if match:
        return match.group(0), "Unknown Module"
    
    return "Unknown", "Unknown Module"


def parse_grades(text: str) -> List[Dict[str, str]]:
    """Parse student grades from extracted text."""
    grades_data = []
    
    # Pattern: Index number (6 digits + letter) followed by grade
    grade_pattern = r'(\d{6}[A-Z])\s+(I-we|I-ca|[A-Z][+-]?|F|D)'
    matches = re.findall(grade_pattern, text)
    
    for index_no, grade in matches:
        grades_data.append({
            'Index_No': sanitize_string(index_no),
            'Grade': sanitize_string(grade)
        })
    
    return grades_data


def process_pdf(pdf_bytes: bytes, filename: str) -> Tuple[Optional[pd.DataFrame], str, str]:
    """
    Process a PDF file and extract grades.
    
    Returns:
        Tuple of (DataFrame with grades, module_code, module_name)
    """
    text = extract_text_from_pdf_bytes(pdf_bytes)
    
    if not text:
        return None, "", ""
    
    module_code, module_name = extract_module_info(text)
    grades_data = parse_grades(text)
    
    if not grades_data:
        return None, module_code, module_name
    
    df = pd.DataFrame(grades_data)
    df['Module_Code'] = module_code
    df['Module_Name'] = module_name
    
    return df, module_code, module_name

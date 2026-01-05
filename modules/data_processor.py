"""
Data processing functions for the UOM Results Ranking Tool.
Handles loading, merging, and SGPA calculation.
"""

import io
from typing import Dict, List, Optional
import pandas as pd
import streamlit as st

from .config import GRADE_POINTS


def load_department_data(file_bytes: bytes, filename: str) -> Optional[pd.DataFrame]:
    """Load department data from uploaded file."""
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
        
        # Validate required column
        if 'Index' not in df.columns:
            st.error("❌ Department file must contain an 'Index' column!")
            return None
        
        return df
    except Exception as e:
        st.error(f"Error loading department file: {e}")
        return None


def merge_grades_with_department(
    dept_df: pd.DataFrame, 
    grades_df: pd.DataFrame,
    module_code: str
) -> pd.DataFrame:
    """Merge grades data with department data."""
    grade_column = f"{module_code}_Grade"
    
    # Prepare grades for merging
    grades_merge = grades_df[['Index_No', 'Grade']].copy()
    grades_merge = grades_merge.rename(columns={'Grade': grade_column})
    
    # Merge with department data
    merged_df = dept_df.merge(
        grades_merge, 
        left_on='Index', 
        right_on='Index_No', 
        how='left'
    )
    
    # Clean up
    if 'Index_No' in merged_df.columns:
        merged_df = merged_df.drop('Index_No', axis=1)
    
    merged_df[grade_column] = merged_df[grade_column].fillna('N/A')
    
    return merged_df


def calculate_sgpa_and_rank(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    """Calculate SGPA and rank for all students."""
    grade_columns = [col for col in df.columns if col.endswith('_Grade')]
    
    def calc_student_sgpa(row):
        total_weighted_points = 0.0
        total_credits = 0.0
        
        for col in grade_columns:
            grade = row[col]
            module_code = col.replace('_Grade', '')
            
            if pd.notna(grade) and grade in GRADE_POINTS and module_code in weights:
                weight = weights[module_code]
                points = GRADE_POINTS[grade]
                total_weighted_points += points * weight
                total_credits += weight
        
        if total_credits == 0:
            return 0.0
        return round(total_weighted_points / total_credits, 3)
    
    df['SGPA'] = df.apply(calc_student_sgpa, axis=1)
    df['Rank'] = df['SGPA'].rank(method='min', ascending=False).astype(int)
    df = df.sort_values('Rank')
    
    return df


def get_existing_modules(df: pd.DataFrame) -> List[str]:
    """Get list of module codes already in the dataframe."""
    grade_columns = [col for col in df.columns if col.endswith('_Grade')]
    return [col.replace('_Grade', '') for col in grade_columns]

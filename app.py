"""
UOM Results Ranking Tool - Streamlit Web Application
A user-friendly tool for non-CS students to process exam results and generate rankings.

Security measures implemented:
- File size limitation (10MB)
- File type validation
- No shell command execution
- Sandboxed file processing
- Input sanitization
- LFI prevention (UUID-based filenames, fixed export directory)
"""

import streamlit as st
import pandas as pd
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Import from modules package
from modules.config import (
    ALLOWED_DEPT_EXTENSIONS, 
    ALLOWED_PDF_EXTENSION,
    EXPORT_CLEANUP_HOURS
)

from modules.security import (
    validate_file_size,
    validate_file_extension,
    cleanup_old_exports,
    save_export_file
)

from modules.pdf_processor import process_pdf

from modules.data_processor import (
    load_department_data,
    merge_grades_with_department,
    calculate_sgpa_and_rank,
    get_existing_modules
)

from modules.ui_components import (
    render_header,
    render_how_it_works,
    render_existing_modules_banner,
    render_footer
)


def main():
    """Main application entry point."""
    render_header()
    render_how_it_works()
    
    # Initialize session state
    if 'department_df' not in st.session_state:
        st.session_state.department_df = None
    if 'weights' not in st.session_state:
        st.session_state.weights = {}
    if 'processed_modules' not in st.session_state:
        st.session_state.processed_modules = []
    
    # =========================================================================
    # STEP 1: Department File Upload
    # =========================================================================
    st.markdown('<div class="step-header"><h3>📁 Step 1: Upload Department File</h3></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Upload your department file containing the student list. This file **must have an `Index` column**.
    Other columns like `Name`, `Email`, `Firstname`, `Lastname` are optional but recommended.
    
    **If you previously exported a file with grades**, upload that to continue building on it!
    """)
    
    dept_file = st.file_uploader(
        "Choose Department File (CSV or Excel)",
        type=['csv', 'xlsx', 'xls'],
        key="dept_uploader",
        help="Maximum file size: 10MB"
    )
    
    if dept_file:
        # Validate file
        is_valid_size, size_msg = validate_file_size(dept_file)
        is_valid_ext, ext_msg = validate_file_extension(dept_file.name, ALLOWED_DEPT_EXTENSIONS)
        
        if not is_valid_size:
            st.error(f"❌ {size_msg}")
        elif not is_valid_ext:
            st.error(f"❌ {ext_msg}")
        else:
            # Only reload department file if it's a NEW file (different name)
            current_dept_file = st.session_state.get('loaded_dept_filename')
            
            if current_dept_file != dept_file.name:
                # New file uploaded - load it
                dept_file.seek(0)
                dept_bytes = dept_file.read()
                df = load_department_data(dept_bytes, dept_file.name)
                
                if df is not None:
                    st.session_state.department_df = df
                    st.session_state.loaded_dept_filename = dept_file.name
                    
                    # Check for existing modules in the NEW file
                    existing_modules = get_existing_modules(df)
                    st.session_state.processed_modules = existing_modules
                    st.session_state.weights = {}
            
            # Display info for loaded department file
            if st.session_state.department_df is not None:
                df = st.session_state.department_df
                
                st.markdown(f"""
                <div class="success-box">
                    <h4>✅ Department File Loaded Successfully!</h4>
                    <p><strong>{len(df)}</strong> students found | 
                    <strong>{len(df.columns)}</strong> columns | 
                    <strong>{len(st.session_state.processed_modules)}</strong> module grades</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show existing modules and weight inputs
                if st.session_state.processed_modules:
                    st.session_state.weights = render_existing_modules_banner(
                        st.session_state.processed_modules, 
                        st.session_state.weights
                    )
                
                # Preview data
                with st.expander("👀 Preview Department Data", expanded=False):
                    st.dataframe(st.session_state.department_df.head(10), use_container_width=True)
    
    # =========================================================================
    # STEP 2: Add Result PDFs
    # =========================================================================
    if st.session_state.department_df is not None:
        st.markdown("---")
        st.markdown('<div class="step-header"><h3>📄 Step 2: Add Result PDFs</h3></div>', unsafe_allow_html=True)
        
        st.markdown("""
        Upload result PDF files one at a time. Each PDF will be processed and the grades will be 
        **appended as a new column** to your data.
        
        🔄 **Remember**: This ADDS to your existing data - it doesn't replace it!
        """)
        
        pdf_file = st.file_uploader(
            "Choose Result PDF",
            type=['pdf'],
            key="pdf_uploader",
            help="Maximum file size: 10MB"
        )
        
        if pdf_file:
            # Validate file
            is_valid_size, size_msg = validate_file_size(pdf_file)
            is_valid_ext, ext_msg = validate_file_extension(pdf_file.name, [ALLOWED_PDF_EXTENSION])
            
            if not is_valid_size:
                st.error(f"❌ {size_msg}")
            elif not is_valid_ext:
                st.error(f"❌ {ext_msg}")
            else:
                # Cache PDF bytes
                pdf_file.seek(0)
                pdf_bytes = pdf_file.read()
                st.session_state['pending_pdf_bytes'] = pdf_bytes
                st.session_state['pending_pdf_name'] = pdf_file.name
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    new_weight = st.number_input(
                        "Enter credit weight for this module:",
                        min_value=0.5,
                        max_value=10.0,
                        value=3.0,
                        step=0.5,
                        key="new_module_weight"
                    )
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    process_btn = st.button("➕ Add This Result", type="primary", use_container_width=True)
                
                if process_btn:
                    with st.spinner("Processing PDF..."):
                        cached_bytes = st.session_state.get('pending_pdf_bytes')
                        cached_name = st.session_state.get('pending_pdf_name', pdf_file.name)
                        
                        if cached_bytes is None or len(cached_bytes) == 0:
                            st.error("❌ Could not read PDF file. Please try uploading again.")
                            st.stop()
                        
                        grades_df, module_code, module_name = process_pdf(cached_bytes, cached_name)
                        
                        if grades_df is None:
                            st.warning(f"Debug: PDF bytes length = {len(cached_bytes)}, Module detected = {module_code}")
                        
                        if grades_df is None or grades_df.empty:
                            st.error("❌ Could not extract grades from PDF. Please check the file format.")
                        else:
                            # Check if module already exists
                            if module_code in st.session_state.processed_modules:
                                st.warning(f"⚠️ Module **{module_code}** already exists. Updating grades.")
                                old_col = f"{module_code}_Grade"
                                if old_col in st.session_state.department_df.columns:
                                    st.session_state.department_df = st.session_state.department_df.drop(columns=[old_col])
                            
                            # Merge grades
                            st.session_state.department_df = merge_grades_with_department(
                                st.session_state.department_df,
                                grades_df,
                                module_code
                            )
                            
                            # Update weights and modules list
                            st.session_state.weights[module_code] = new_weight
                            if module_code not in st.session_state.processed_modules:
                                st.session_state.processed_modules.append(module_code)
                            
                            st.success(f"""
                            ✅ **{module_code} - {module_name}** added successfully!
                            - {len(grades_df)} grades extracted from PDF
                            - Weight set to **{new_weight}** credits
                            """)
                            
                            st.rerun()
        
        # Show current modules summary
        if st.session_state.processed_modules:
            st.markdown("---")
            st.markdown("### 📋 Current Modules in Your Data")
            
            module_info = []
            for module in st.session_state.processed_modules:
                weight = st.session_state.weights.get(module, "Not set")
                grade_col = f"{module}_Grade"
                if grade_col in st.session_state.department_df.columns:
                    grades_found = (st.session_state.department_df[grade_col] != 'N/A').sum()
                else:
                    grades_found = 0
                module_info.append({
                    "Module Code": module,
                    "Weight (Credits)": weight,
                    "Grades Found": grades_found
                })
            
            st.dataframe(pd.DataFrame(module_info), use_container_width=True, hide_index=True)
    
    # =========================================================================
    # STEP 4: Generate Rankings
    # =========================================================================
    if st.session_state.department_df is not None and st.session_state.processed_modules:
        st.markdown("---")
        st.markdown('<div class="step-header"><h3>🏆 Step 4: Generate Rankings</h3></div>', unsafe_allow_html=True)
        
        # Check if all weights are set
        all_weights_set = all(
            module in st.session_state.weights 
            for module in st.session_state.processed_modules
        )
        
        if not all_weights_set:
            st.warning("⚠️ Please set weights for all modules before generating rankings.")
        else:
            if st.button("🚀 Generate SGPA & Rankings", type="primary", use_container_width=True):
                with st.spinner("Calculating SGPA and generating rankings..."):
                    result_df = calculate_sgpa_and_rank(
                        st.session_state.department_df.copy(),
                        st.session_state.weights
                    )
                    st.session_state.result_df = result_df
                    st.session_state.ranking_generated = True
                    st.info(f"📊 Generated rankings for {len(result_df)} students with {len(result_df.columns)} columns")
            
            # Display results if they exist
            if st.session_state.get('ranking_generated') and st.session_state.get('result_df') is not None:
                result_df = st.session_state.result_df
                
                st.markdown("""
                <div class="success-box">
                    <h4>🎉 Rankings Generated Successfully!</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Students", len(result_df))
                with col2:
                    st.metric("Highest SGPA", f"{result_df['SGPA'].max():.3f}")
                with col3:
                    st.metric("Average SGPA", f"{result_df['SGPA'].mean():.3f}")
                with col4:
                    st.metric("Modules Used", len(st.session_state.processed_modules))
                
                # Display results
                st.markdown("### 📊 Top 20 Students")
                display_cols = ['Rank', 'Index']
                if 'Name' in result_df.columns:
                    display_cols.append('Name')
                if 'Firstname' in result_df.columns and 'Lastname' in result_df.columns:
                    display_cols.extend(['Firstname', 'Lastname'])
                display_cols.append('SGPA')
                display_cols.extend([f"{m}_Grade" for m in st.session_state.processed_modules])
                
                display_cols = [c for c in display_cols if c in result_df.columns]
                st.dataframe(result_df[display_cols].head(20), use_container_width=True, hide_index=True)
                
                # Download buttons
                st.markdown("### 📥 Download Results")
                
                cleanup_old_exports(max_age_hours=EXPORT_CLEANUP_HOURS)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    try:
                        csv_filename, csv_filepath = save_export_file(result_df, 'csv')
                        with open(csv_filepath, 'rb') as f:
                            csv_data = f.read()
                        st.download_button(
                            label="📄 Download as CSV",
                            data=csv_data,
                            file_name="ranked_results.csv",
                            mime="text/csv",
                            use_container_width=True,
                            key="download_csv"
                        )
                    except Exception as e:
                        st.error(f"Error creating CSV: {e}")
                
                with col2:
                    try:
                        xlsx_filename, xlsx_filepath = save_export_file(result_df, 'xlsx')
                        with open(xlsx_filepath, 'rb') as f:
                            xlsx_data = f.read()
                        st.download_button(
                            label="📊 Download as Excel",
                            data=xlsx_data,
                            file_name="ranked_results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key="download_excel"
                        )
                    except Exception as e:
                        st.error(f"Error creating Excel: {e}")
    
    # Footer
    render_footer()


if __name__ == "__main__":
    main()

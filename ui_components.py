"""
UI components for the UOM Results Ranking Tool.
Contains all Streamlit UI rendering functions.
"""

import streamlit as st
from typing import Dict, List


def render_header():
    """Render the application header."""
    st.set_page_config(
        page_title="UOM Results Ranking Tool",
        page_icon="📊",
        layout="wide"
    )
    
    st.markdown("""
    <style>
        /* Main header - works in both modes */
        .main-header {
            text-align: center;
            padding: 1.5rem 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .main-header h1, .main-header p {
            color: white !important;
            margin: 0.5rem 0;
        }
        
        /* Info boxes - dark mode compatible */
        .info-box {
            background-color: rgba(33, 150, 243, 0.15);
            border-left: 4px solid #2196F3;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
            color: inherit;
        }
        .warning-box {
            background-color: rgba(255, 193, 7, 0.15);
            border-left: 4px solid #ffc107;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
            color: inherit;
        }
        .warning-box h4 {
            color: #ffc107 !important;
        }
        .success-box {
            background-color: rgba(40, 167, 69, 0.15);
            border-left: 4px solid #28a745;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
            color: inherit;
        }
        .success-box h4 {
            color: #28a745 !important;
        }
        
        /* Module chips */
        .module-chip {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            padding: 0.4rem 0.9rem;
            border-radius: 20px;
            margin: 0.3rem;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        /* Step headers - dark mode compatible */
        .step-header {
            background: rgba(102, 126, 234, 0.1);
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin: 1.5rem 0 1rem 0;
            border-left: 4px solid #667eea;
        }
        .step-header h3 {
            color: inherit !important;
            margin: 0;
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
        }
        
        /* Ensure text visibility in dark mode */
        @media (prefers-color-scheme: dark) {
            .info-box, .warning-box, .success-box {
                color: #e0e0e0;
            }
            .step-header {
                background: rgba(102, 126, 234, 0.2);
            }
        }
        
        /* For Streamlit's internal dark mode */
        [data-testid="stAppViewContainer"][data-theme="dark"] .info-box,
        [data-testid="stAppViewContainer"][data-theme="dark"] .warning-box,
        [data-testid="stAppViewContainer"][data-theme="dark"] .success-box {
            color: #e0e0e0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>📊 UOM Results Ranking Tool</h1>
        <p>Easily process exam results and generate student rankings</p>
    </div>
    """, unsafe_allow_html=True)


def render_how_it_works():
    """Render the 'How It Works' section."""
    with st.expander("📖 How This Tool Works (Click to learn more)", expanded=True):
        st.markdown("""
        ### 🔄 Understanding the Append Behavior
        
        This tool is designed to **build your result sheet progressively**. Here's what you need to know:
        
        1. **📁 Department File** - Upload this ONCE. It contains your student list with Index numbers.
        
        2. **📄 Result PDFs** - Add them ONE BY ONE. Each PDF you add will:
           - ✅ **Automatically detect** the module code from the PDF
           - ✅ **Append the grades** as a new column to your existing data
           - ✅ **Preserve all previously added** module grades
        
        3. **⚖️ Weights** - You must set credit weights for:
           - New modules you're adding
           - **AND all previously added modules** (if any exist)
        
        ---
        
        ### 📝 Example Workflow:
        
        | Step | Action | Result |
        |------|--------|--------|
        | 1 | Upload `Batch23_CSE.xlsx` | Student list loaded (Index, Name, Email) |
        | 2 | Add `CS1040_Results.pdf` with weight 3 | Now has: Index, Name, Email, **CS1040_Grade** |
        | 3 | Add `MA1024_Results.pdf` with weight 3 | Now has: Index, Name, Email, CS1040_Grade, **MA1024_Grade** |
        | 4 | Generate Ranking | SGPA calculated, Rank assigned! |
        
        ---
        
        ⚠️ **Important**: Each time you use this tool in a new session, upload your **most recent department file** 
        (the one that already has previous module grades) to continue building on it!
        """)


def render_existing_modules_banner(modules: List[str], weights: Dict[str, float]) -> Dict[str, float]:
    """Show banner for existing modules in the department file and allow setting weights."""
    if not modules:
        return weights
    
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Previously Added Modules Detected!</h4>
        <p>Your department file already contains grades for these modules. 
        <strong>Set weights for ALL of them below</strong> to calculate the correct SGPA.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show modules as chips for visual reference
    chips_html = ""
    for module in modules:
        weight_str = f" ({weights.get(module, '?')} credits)" if module in weights else " (⚠️ set below)"
        chips_html += f'<span class="module-chip">{module}{weight_str}</span>'
    
    st.markdown(f"<p>{chips_html}</p>", unsafe_allow_html=True)
    
    # Immediately show weight inputs for existing modules
    st.markdown("#### ⚖️ Set Weights for Existing Modules")
    st.caption("💡 Enter the credit value for each module (common values: 2 or 3)")
    
    updated_weights = weights.copy()
    num_cols = min(len(modules), 4)
    cols = st.columns(num_cols)
    
    for i, module in enumerate(modules):
        col_idx = i % num_cols
        with cols[col_idx]:
            default_val = weights.get(module, 3.0)
            updated_weights[module] = st.number_input(
                f"**{module}**",
                min_value=0.5,
                max_value=10.0,
                value=float(default_val),
                step=0.5,
                key=f"existing_weight_{module}"
            )
    
    return updated_weights


def render_weight_input(modules: List[str], existing_weights: Dict[str, float]) -> Dict[str, float]:
    """Render weight input section for modules."""
    st.markdown("### ⚖️ Set Module Weights (Credits)")
    
    st.info("💡 **Tip**: Enter the credit value for each module. Common values: 2 or 3 credits.")
    
    weights = {}
    cols = st.columns(min(len(modules), 4))
    
    for i, module in enumerate(modules):
        col_idx = i % len(cols)
        with cols[col_idx]:
            default_val = existing_weights.get(module, 3.0)
            weights[module] = st.number_input(
                f"**{module}**",
                min_value=0.5,
                max_value=10.0,
                value=float(default_val),
                step=0.5,
                key=f"weight_{module}"
            )
    
    return weights


def render_footer():
    """Render the application footer."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Made with ❤️ for UOM Students</p>
    </div>
    """, unsafe_allow_html=True)

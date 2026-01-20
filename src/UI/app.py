import streamlit as st
import sys
import os
import time

# --- PATH FIX ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.parsing.chunker import SafeChunker
from src.agents.refinery_agent import RefineryAgent
from src.utils.jupyter_builder import JupyterBuilder
from src.parsing.converter import notebook_to_markdown # <--- NEW IMPORT

st.set_page_config(page_title="DocForge Workbench", page_icon="⚒️", layout="wide")

st.title("⚒️ DocForge: The Refinery")

# ==============================================================================
# SIDEBAR: PROJECT MANAGER
# ==============================================================================
st.sidebar.header("📂 Project Manager")
PROJECTS_ROOT = "data/projects"
os.makedirs(PROJECTS_ROOT, exist_ok=True)

existing_projects = [f for f in os.listdir(PROJECTS_ROOT) if os.path.isdir(os.path.join(PROJECTS_ROOT, f))]
active_project = st.sidebar.selectbox("Active Project", ["Default"] + existing_projects)

with st.sidebar.expander("Create New Project"):
    new_proj_name = st.text_input("Project Name")
    if st.button("Create Project"):
        if new_proj_name:
            os.makedirs(os.path.join(PROJECTS_ROOT, new_proj_name), exist_ok=True)
            st.rerun()

project_path = os.path.join(PROJECTS_ROOT, active_project)
os.makedirs(project_path, exist_ok=True)
st.sidebar.success(f"Active: {active_project}")

# ==============================================================================
# TAB 1: THE REFINERY
# ==============================================================================
tab1, tab2 = st.tabs(["🔥 The Refinery (Migration)", "📉 Drift Monitor (Legacy)"])

with tab1:
    st.header("Legacy Documentation Migration")
    st.markdown("Upload **Markdown** or **Jupyter Notebooks**. We will refine them to Google Style.")
    
    # 1. UPDATED: Accept both .md and .ipynb
    uploaded_file = st.file_uploader("Upload Legacy File", type=["md", "ipynb"])
    
    if uploaded_file:
        # Save original file
        file_path = os.path.join(project_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.info(f"Loaded: {uploaded_file.name}")
        
        if st.button("Start Refinery Process", type="primary"):
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            # 2. UPDATED: Normalize Input
            status_box.text("Normalizing input format...")
            
            if uploaded_file.name.endswith(".ipynb"):
                # Convert NB -> Markdown String
                content = notebook_to_markdown(uploaded_file.getvalue())
            else:
                # Read MD directly
                content = uploaded_file.getvalue().decode("utf-8")
            
            # --- The Standard Pipeline (Unchanged) ---
            chunker = SafeChunker(max_tokens=1000)
            refiner = RefineryAgent()
            builder = JupyterBuilder()
            
            chunks = list(chunker.chunk_file(content))
            total_chunks = len(chunks)
            
            if total_chunks == 0:
                st.error("No content found or file is empty.")
                st.stop()
            
            st.write(f"Detected {total_chunks} chunks. Processing safely in serial...")
            results_container = st.container()
            
            for i, chunk in enumerate(chunks):
                progress = (i + 1) / total_chunks
                progress_bar.progress(progress)
                status_box.text(f"Processing Chunk {i+1}/{total_chunks}...")
                
                raw_text = chunk['content']
                refined_text = refiner.refine_chunk(raw_text)
                builder.add_content(refined_text)
                
                with results_container:
                    with st.expander(f"Chunk {i+1} Result", expanded=False):
                        col_a, col_b = st.columns(2)
                        col_a.text_area("Original", raw_text, height=150, key=f"orig_{i}")
                        col_b.text_area("Refined", refined_text, height=150, key=f"ref_{i}")
                
            # Finalize
            output_filename = f"{os.path.splitext(uploaded_file.name)[0]}_refined.ipynb"
            output_path = os.path.join(project_path, output_filename)
            builder.save(output_path)
            
            status_box.success("✅ Migration Complete!")
            st.balloons()
            
            with open(output_path, "r") as f:
                st.download_button(
                    label="Download Refined Notebook",
                    data=f,
                    file_name=output_filename,
                    mime="application/json"
                )

# ==============================================================================
# TAB 2: DRIFT MONITOR
# ==============================================================================
with tab2:
    st.caption("Drift Monitor is currently disabled in this view.")
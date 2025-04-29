# home.py
import os, sys, streamlit as st

ROOT = os.path.abspath(os.path.dirname(__file__))
SRC  = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

st.set_page_config(page_title="RDD Metabolomics", page_icon="🧬", layout="wide")

st.title("Reference Data-Driven (RDD) Metabolomics App")
st.markdown(
    """
Use the sidebar to:  
1. **Create** an RDD count table  
2. **Visualise** bar / box / heat maps  
3. **Run PCA**  
4. **Explore Sankey** flows  

All data stay in *session_state* until you refresh the browser tab.
"""
)

if "rdd" in st.session_state:
    st.success("RDDCounts object is already in memory ✅")
else:
    st.info("⬅️ Head to **Create RDD Count Table** to begin")
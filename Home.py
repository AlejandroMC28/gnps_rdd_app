# home.py
import os, sys, streamlit as st
from pathlib import Path

# ---------------------------------------------------------------------
#  Boiler‑plate: make “src/” importable
# ---------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

# ---------------------------------------------------------------------
#  Page config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="RDD Metabolomics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Helper to build internal links (works in local & Cloud run)
def _page_url(stem: str) -> str:  # e.g.  '05_How_to_Use'
    return f"./{stem}"


# ---------------------------------------------------------------------
#  TITLE  &  INTRO
# ---------------------------------------------------------------------
st.title("Reference Data‑Driven (RDD) Metabolomics app")

st.write(
    """
This application turns untargeted LC‑MS data into **actionable biological
insight** by matching your spectra against richly annotated **reference
libraries**.
"""
)


# ---------------------------------------------------------------------
#  WHAT THE APP CAN DO
# ---------------------------------------------------------------------
st.header("What can I do with the app?")

st.markdown(
    """
1. **Create an RDD count table** from a GNPS molecular network  
2. **Explore & visualise** any ontology level (bar / box / heat maps)  
3. **Run PCA** (with optional CLR transform) in one click  
4. **Trace hierarchical flows** with an interactive Sankey diagram  
"""
)
st.markdown(
    """
### 📁 What data do I need?
- **GNPS network data** (required): Your molecular networking results
- **Reference metadata** (required): Preloaded foodomics library by default, or upload your own
- **Sample metadata** (optional for GNPS1, necessary for GNPS2): Define your experimental groups
"""
)
st.success(f"👋 First time here? Have a look at the " f"How to use page.")

# ---------------------------------------------------------------------
#  SESSION‑STATE REMINDER
# ---------------------------------------------------------------------
if "rdd" in st.session_state:
    st.success("RDDCounts object detected — you’re ready to explore ✅")
else:
    st.info("⬅️ Go to **Create RDD Count Table** in the sidebar to begin.")

# pages/05_How_to_Use.py
import streamlit as st

st.header("How to Use / About")

st.markdown(
    """
**Quick Start with Demo Data**

- Click **"Use Demo Data"** on the *Create RDD Count Table* page to instantly load example GNPS network and metadata files.
- The demo data lets you apply RDD to dietary data. Explore different dietary groups and their RDD profiles
- After generating the count table, the app will automatically apply a demo sample metadata file to assign groups to each sample. This enables group-based analyses (like PCA and plots) even if you don't have your own metadata.
- To return to your own data, simply reload the page.

---

**Workflow Steps**

1. **Create RDD Count Table**  
   Upload a GNPS network and (optionally) metadata, choose parameters, and click *Generate*.  
   An `RDDCounts` object is stored in *session_state* for use in all other pages.

2. **Visualizations**  
   Select ontology level, reference types, and backend to generate bar, box, or heat maps.

3. **PCA Analysis**  
   Optionally apply CLR transformation and visualize principal components by group.

4. **Sankey Diagram**  
   Provide a colour map (`descriptor;color_code`) and explore hierarchical flows.

---

**Tip:**  
After generating the count table, you can upload a mapping file to change group assignments for your samples. The mapping file should have columns: `filename` and `new_group`.
"""
)

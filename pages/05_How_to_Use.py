# pages/05_How_to_Use.py
import streamlit as st

st.header("How to Use / About")

st.markdown(
    """
**Quick Start with Demo Data**

- Click **"Use Demo Data"** on the *Create RDD Count Table* page to instantly load example GNPS network and metadata files.
- The demo data lets you apply RDD to dietary data. Explore different dietary groups and their RDD profiles.
- After generating the count table, the app will automatically apply a demo sample metadata file to assign groups to each sample. This enables group-based analyses (like PCA and plots) even if you don't have your own metadata.
- To return to your own data, simply reload the page.

---

**Workflow Steps**

1. **Create RDD Count Table**  
   You have two options for data input:
   
   **Option A: Upload File**
   - Upload a GNPS molecular network file (.csv or .tsv)
   - Optionally upload sample and reference metadata
   - Choose sample groups from your GNPS network (e.g., G1, G2)
   
   **Option B: GNPS Task ID**
   - Enter your GNPS job task ID (found in your GNPS job URL)
   - Select GNPS version (GNPS2 or GNPS1 Classic)
   - Sample metadata is **required** when using task ID to define sample groups
   - The app will fetch the network data directly from GNPS servers
   
   After selecting your input method, choose parameters and click *Generate*.  
   An `RDDCounts` object is stored in *session_state* for use in all other pages.

2. **Visualizations**  
   Select ontology level, reference types, and backend to generate bar, box, or heat maps.

3. **PCA Analysis**  
   Optionally apply CLR transformation and visualize principal components by group.

4. **Sankey Diagram**  
   Provide a colour map (`descriptor;color_code`) and explore hierarchical flows.

---

**Tips:**

- **GNPS Task ID Format**: Your task ID looks like `b93a540abded417ab1e2a285544a148c` and can be found in your GNPS job URL.
- **Metadata Requirements**: When using GNPS Task ID, you must upload sample metadata to define which samples belong to which groups.
- **Group Remapping**: After generating the count table, you can upload a mapping file to change group assignments. The mapping file should have columns: `filename` and `new_group`.
"""
)

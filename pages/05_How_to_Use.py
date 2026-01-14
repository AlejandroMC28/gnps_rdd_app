# pages/05_How_to_Use.py
import streamlit as st

st.header("How to Use / About")

st.markdown(
    """
**Quick Start with Demo Data**

- Click **"Use Demo Data"** on the *Create RDD Count Table* page to instantly load example GNPS network, sample metadata, and reference metadata files.
- The demo data demonstrates RDD analysis of dietary data with Omnivore vs Vegan groups.
- Explore different dietary groups and their RDD profiles across the foodomics ontology hierarchy.
- To return to your own data, simply reload the page.

---

**Understanding the Required Data**

**What is RDD Metabolomics?**  
Reference Data-Driven (RDD) metabolomics matches your experimental spectra against annotated reference libraries to quantify biological features across hierarchical ontologies.

**Three Types of Data:**

1. **GNPS Network Data** (Required)
   - Your molecular networking results from GNPS
   - Contains spectral similarity information and library matches
   - Can be uploaded as a file or fetched via GNPS Task ID

2. **Reference Metadata** (Preloaded by Default)
   - Links reference spectra to their known biological origins using hierarchical ontologies
   - **Default behavior:** Uses preloaded foodomics reference library with food classifications
   - **Custom option:** Upload your own reference metadata for non-food studies
   - **Format:** Must include `filename` column + hierarchical ontology columns (e.g., `kingdom`, `phylum`, `class`)
   - **Access in code:** After creating RDDCounts object, available as `rdd.reference_metadata`

3. **Sample Metadata** (Required for GNPS2, Optional for GNPS1/File Upload)
   - Maps your sample files to experimental groups (e.g., treatment vs control, disease vs healthy)
   - **For GNPS2:** Always required to define sample groupings
   - **For GNPS1/File Upload:** Can use DefaultGroups from network file if not provided
   - **Format:** Must include `filename` column + `group` column (or your chosen grouping column)
   - **Access in code:** After creating RDDCounts object, available as `rdd.sample_metadata`

---

**Workflow Steps**

1. **Create RDD Count Table**  
   You have two options for data input:
   
   **Option A: Upload File**
   - Upload a GNPS molecular network file (.csv or .tsv)
   - Optionally upload sample metadata (recommended for custom groups)
   - Optionally upload reference metadata (uses foodomics library if not provided)
   - Choose sample groups from your data
   
   **Option B: GNPS Task ID**
   - Enter your GNPS job task ID (found in your GNPS job URL)
   - Select GNPS version (GNPS2 or GNPS1 Classic)
   - **GNPS2 requires sample metadata** to define sample groups
   - **GNPS1 can use DefaultGroups** from network or accept custom sample metadata
   - Optionally upload reference metadata (uses foodomics library if not provided)
   - The app will fetch the network data directly from GNPS servers
   
   After selecting your input method, choose parameters and click *Generate*.  
   An `RDDCounts` object is stored in *session_state* for use in all other pages.
   
   **Viewing Loaded Metadata:**  
   After generation, the app displays summaries of your loaded reference and sample metadata,
   including the number of ontology levels, grouping information, and preview tables.

2. **Visualizations**  
   Select ontology level, reference types, and backend to generate bar, box, or heat maps.

3. **PCA Analysis**  
   Optionally apply CLR transformation and visualize principal components by group.

4. **Sankey Diagram**  
   Provide a colour map (`descriptor;color_code`) and explore hierarchical flows.

---

**Tips:**

- **GNPS Task ID Format**: Your task ID looks like `b93a540abded417ab1e2a285544a148c` and can be found in your GNPS job URL.
- **GNPS2 Requirements**: Always requires sample metadata with `filename` and `group` columns.
- **Default Reference Library**: The preloaded foodomics metadata contains hierarchical food classifications across multiple ontology levels.
- **Custom Metadata**: For non-food metabolomics, upload your own reference metadata with appropriate ontology columns.
- **Group Remapping**: After generating the count table, you can upload a mapping file to change group assignments. The mapping file should have columns: `filename` and `new_group`.
- **Accessing Metadata**: Use `rdd.reference_metadata` and `rdd.sample_metadata` to view or export your loaded metadata as pandas DataFrames.
"""
)

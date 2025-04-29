# pages/05_How_to_Use.py
import streamlit as st

st.header("How to Use / About")

st.markdown(
    """
**Steps**

1. **Create RDD Count Table**  
   Upload a GNPS network and metadata, choose parameters, click *Generate*.  
   An `RDDCounts` object is stored in *session_state*.

2. **Visualizations**  
   Select ontology level, reference types, backend, generate bar/box/heat maps.

3. **PCA Analysis**  
   CLR-transform (optional) and visualise principal components.

4. **Sankey Diagram**  
   Provide a colour map (`descriptor;color_code`) and explore hierarchical flows.

**Session reset**  
When you refresh the browser tab the session clears. Use *Download / Upload* (not yet implemented) or re-run the “Create” step.

**Source code**  
All visual logic resides in your existing `src.visualization` module; the Streamlit pages merely call those helpers.
"""
)

"""
Helpers that *touch Streamlit session state* but leave your core library
(src.RDDcounts, utils, analysis, visualization) completely untouched.
"""

from typing import Any
import streamlit as st


def set_group(rdd: Any, column_name: str) -> None:
    """
    Make `column_name` the active grouping column.

    • Saves the choice in st.session_state["group_column"]
    • Adds / overwrites a view-only column called **'group'** in both
      rdd.sample_metadata and rdd.counts, so every plotting routine
      (which expects a literal 'group') just works.

    Parameters
    ----------
    rdd : RDDCounts
        The RDDCounts instance stored in st.session_state["rdd"].
    column_name : str
        Column in rdd.sample_metadata to treat as grouping column.
    """
    if column_name not in rdd.sample_metadata.columns:
        st.error(f"Column '{column_name}' not found in sample metadata.")
        return

    st.session_state["group_column"] = column_name

    # Map to canonical 'group' in sample_metadata
    rdd.sample_metadata["group"] = rdd.sample_metadata[column_name].astype(str)

    # Map to 'group' in counts via filename
    mapping = rdd.sample_metadata.set_index("filename")["group"]
    rdd.counts["group"] = rdd.counts["filename"].map(mapping)

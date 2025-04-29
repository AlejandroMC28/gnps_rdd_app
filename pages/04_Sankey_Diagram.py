# pages/04_Sankey_Diagram.py
import os
import sys

import streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from src.visualization import Visualizer, PlotlyBackend  # noqa: E402
from src.RDDcounts import RDDCounts  # noqa: E402

st.header("Sankey Diagram")

if "rdd" not in st.session_state:
    st.warning("Please create an RDDCounts object first.")
    st.stop()

rdd: RDDCounts = st.session_state["rdd"]

# ---------- controls ---------- #
sample = st.selectbox(
    "Filter by sample filename (optional)",
    options=["<all samples>"] + sorted(rdd.counts["filename"].unique().tolist()),
)
max_level = st.number_input(
    "Maximum hierarchy level (blank = all)",
    min_value=1,
    max_value=rdd.levels,
    step=1,
    value=rdd.levels,
)
color_csv = st.file_uploader(
    "Color mapping CSV (`descriptor;color_code`)", type=("csv", "txt", "tsv")
)
dark_mode = st.checkbox("Dark mode", value=False)
draw = st.button("Draw Sankey")

# ---------- plot ---------- #
if draw:
    if color_csv is None:
        st.error("Please upload a color-mapping CSV.")
        st.stop()

    # Save color mapping to temp
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(color_csv.read())
        color_path = tmp.name

    viz = Visualizer(PlotlyBackend())
    fig = viz.plot_sankey(
        RDD_counts=rdd,
        color_mapping_file=color_path,
        max_hierarchy_level=max_level or None,
        filename_filter=None if sample == "<all samples>" else sample,
        dark_mode=dark_mode,
    )
    st.plotly_chart(fig, use_container_width=True)

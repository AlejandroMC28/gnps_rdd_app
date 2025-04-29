# pages/04_Sankey_Diagram.py
import os, sys, tempfile, streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from src.visualization import Visualizer, PlotlyBackend  # noqa: E402

st.header("Sankey Diagram")

# ── guard: need the RDDCounts object ───────────────────────────────────
if "rdd" not in st.session_state:
    st.warning("Please create an RDD count table first.")
    st.stop()

rdd = st.session_state["rdd"]
viz = Visualizer(PlotlyBackend())  # Sankey supported only in Plotly

# ── user controls ──────────────────────────────────────────────────────
sample_choice = st.selectbox(
    "Filter by sample filename (optional)",
    ["<all samples>"] + sorted(rdd.counts["filename"].unique()),
)

max_level = st.number_input(
    "Maximum hierarchy level", 1, rdd.levels, rdd.levels, step=1
)

color_map_up = st.file_uploader(
    "Colour-mapping CSV (`descriptor;color_code`, optional)", type=("csv", "tsv", "txt")
)

dark_mode = st.checkbox("Dark mode")

# ── draw button ────────────────────────────────────────────────────────
if st.button("Draw Sankey"):
    # persist colour map only if provided
    colour_path = None
    if color_map_up:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(color_map_up.getbuffer())
            colour_path = tmp.name

    fig = viz.plot_sankey(
        rdd,
        color_mapping_file=colour_path,  # may be None
        max_hierarchy_level=max_level or None,
        filename_filter=None if sample_choice == "<all samples>" else sample_choice,
        dark_mode=dark_mode,
    )
    st.plotly_chart(fig, use_container_width=True)

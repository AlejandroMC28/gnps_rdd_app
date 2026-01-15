# pages/02_Visualizations.py
import os, sys, streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from rdd.visualization import Visualizer, PlotlyBackend, MatplotlibBackend  # noqa: E402

if "rdd" not in st.session_state:
    st.warning("First create an RDDCounts object.")
    st.stop()

rdd = st.session_state["rdd"]

# Show current grouping info (read-only)
if st.session_state.get("custom_mapping_applied", False):
    st.info("📊 **Custom group mapping applied** (Change via mapping file on page 1)")
else:
    st.info("📊 **Using original groups** (Apply custom mapping on page 1)")

backend_choice = st.radio("Backend", ("Plotly", "Matplotlib"), horizontal=True)
backend = PlotlyBackend() if backend_choice == "Plotly" else MatplotlibBackend()
viz = Visualizer(backend)

level = st.slider("Ontology level", 0, rdd.levels, 3)

default_types = rdd.counts.query("level==@level")["reference_type"].unique().tolist()
sel_types = st.multiselect("Reference types (blank = all)", default_types)

group_toggle = st.checkbox("Group by", value=True)
if st.button("Render plots"):
    tab_bar, tab_box, tab_heat = st.tabs(["Barplot", "Boxplot", "Heatmap"])

    with tab_bar:
        fig = viz.plot_reference_type_distribution(
            rdd, level, sel_types or None, group_by=group_toggle
        )
        (st.plotly_chart if backend_choice == "Plotly" else st.pyplot)(
            fig, use_container_width=True
        )

    with tab_box:
        fig = viz.box_plot_RDD_proportions(rdd, level, sel_types or None, group_by=group_toggle)
        (st.plotly_chart if backend_choice == "Plotly" else st.pyplot)(
            fig, use_container_width=True
        )

    with tab_heat:
        fig = viz.plot_RDD_proportion_heatmap(rdd, level, sel_types or None)
        (st.plotly_chart if backend_choice == "Plotly" else st.pyplot)(
            fig, use_container_width=True
        )

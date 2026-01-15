# pages/03_PCA_Analysis.py
import os, sys, streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from rdd.analysis import perform_pca_RDD_counts  # noqa: E402
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

level = st.slider("Ontology level", 0, rdd.levels, 3)
apply_clr = st.checkbox("Apply CLR transformation", True)
backend_choice = st.radio("Backend", ("Plotly", "Matplotlib"), horizontal=True)

if st.button("Run PCA"):
    pca_df, ev = perform_pca_RDD_counts(rdd, level=level, apply_clr=apply_clr)

    backend = PlotlyBackend() if backend_choice == "Plotly" else MatplotlibBackend()
    viz = Visualizer(backend)

    fig_scatter = viz.plot_pca_results(pca_df, ev, group_by=True, group_column="group")
    fig_ev = viz.plot_explained_variance(ev)

    (st.plotly_chart if backend_choice == "Plotly" else st.pyplot)(
        fig_scatter, use_container_width=True
    )
    (st.plotly_chart if backend_choice == "Plotly" else st.pyplot)(fig_ev, use_container_width=True)

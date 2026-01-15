# pages/04_Sankey_Diagram.py
import os, sys, tempfile, streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from rdd.visualization import Visualizer, PlotlyBackend  # noqa: E402

st.header("Sankey Diagram")

# ── guard: need the RDDCounts object ───────────────────────────────────
if "rdd" not in st.session_state:
    st.warning("Please create an RDD count table first.")
    st.stop()

rdd = st.session_state["rdd"]
viz = Visualizer(PlotlyBackend())  # Sankey supported only in Plotly

# ── guard: need at least 2 ontology levels for Sankey ─────────────────
if rdd.levels < 2:
    st.warning(
        "⚠️ Sankey diagrams require at least 2 ontology levels to visualize hierarchical flows."
    )
    st.info(
        f"Current RDD object has {rdd.levels} level(s). Please create an RDD count table with levels ≥ 2."
    )
    st.stop()

# ── user controls ──────────────────────────────────────────────────────
sample_choice = st.selectbox(
    "Filter by sample filename (optional)",
    ["<all samples>"] + sorted(rdd.counts["filename"].unique()),
)

max_level = st.number_input("Maximum hierarchy level", 1, rdd.levels, rdd.levels, step=1)


def load_demo_file(filename):
    import io

    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(ROOT, "data", filename)
    with open(path, "rb") as f:
        file_obj = io.BytesIO(f.read())
        file_obj.name = filename
        return file_obj


color_map_up = None
if st.session_state.get("use_demo"):
    # Automatically use demo color map if in demo mode - clean it to 2 columns
    try:
        import pandas as pd
        import io

        demo_file = load_demo_file("sample_type_hierarchy.csv")
        color_df = pd.read_csv(demo_file, sep=";")

        # Keep only descriptor and color_code columns
        if "descriptor" in color_df.columns and "color_code" in color_df.columns:
            color_df = color_df[["descriptor", "color_code"]]

        # Convert back to BytesIO
        csv_str = color_df.to_csv(index=False, sep=";")
        color_map_up = io.BytesIO(csv_str.encode())
        color_map_up.name = "sample_type_hierarchy.csv"
        st.info("Demo color map loaded automatically.")
    except Exception as e:
        st.warning(f"Demo color map not found: {e}")
else:
    color_option = st.radio(
        "Color mapping option",
        ["Use foodomics color mapping", "Upload custom file", "Use grayscale"],
        horizontal=True,
    )

    if color_option == "Use foodomics color mapping":
        # Use the default foodomics color mapping - clean to 2 columns
        try:
            import pandas as pd
            import io

            demo_file = load_demo_file("sample_type_hierarchy.csv")
            color_df = pd.read_csv(demo_file, sep=";")

            # Keep only descriptor and color_code columns
            if "descriptor" in color_df.columns and "color_code" in color_df.columns:
                color_df = color_df[["descriptor", "color_code"]]

            # Convert back to BytesIO
            csv_str = color_df.to_csv(index=False, sep=";")
            color_map_up = io.BytesIO(csv_str.encode())
            color_map_up.name = "sample_type_hierarchy.csv"
            st.info("✓ Using foodomics reference color mapping")
        except Exception as e:
            st.error(f"Could not load foodomics color mapping: {e}")
    elif color_option == "Upload custom file":
        color_map_up = st.file_uploader(
            "Colour-mapping file (CSV/TSV with 2 columns: descriptor and color_code)",
            type=("csv", "tsv", "txt"),
        )
    else:
        # Generate grayscale mapping automatically
        import io
        import pandas as pd

        # Get all unique reference types from level 0
        unique_types = rdd.counts[rdd.counts["level"] == 0]["reference_type"].unique()
        n_types = len(unique_types)

        # Generate grayscale colors
        grayscale_colors = [
            f"#{int(255 - (i * 200 / max(n_types-1, 1))):02x}" * 3 for i in range(n_types)
        ]

        # Create mapping dataframe
        color_df = pd.DataFrame({"descriptor": unique_types, "color_code": grayscale_colors})

        # Convert to BytesIO object (with header to match expected format)
        csv_str = color_df.to_csv(index=False, sep=";", header=True)
        color_map_up = io.BytesIO(csv_str.encode())
        color_map_up.name = "grayscale_mapping.csv"
        st.info(f"✓ Generated grayscale mapping for {n_types} reference types")

dark_mode = st.checkbox("Dark mode")

# ── draw button ────────────────────────────────────────────────────────
if st.button("Draw Sankey"):
    if not color_map_up:
        st.error("⚠️ Please select a color mapping option.")
        st.stop()

    # Read uploaded file and convert to semicolon-separated format for backend
    import pandas as pd
    import io

    try:
        # Try to read with common separators
        color_map_up.seek(0)
        content = color_map_up.read().decode("utf-8")

        # Detect separator and read
        if ";" in content.split("\n")[0]:
            sep = ";"
        elif "\t" in content.split("\n")[0]:
            sep = "\t"
        else:
            sep = ","

        color_map_up.seek(0)
        color_df = pd.read_csv(color_map_up, sep=sep)

        # Ensure we have the expected columns
        if len(color_df.columns) >= 2:
            color_df = color_df.iloc[:, :2]  # Take first two columns
            color_df.columns = ["descriptor", "color_code"]

        # Save as semicolon-separated for backend
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as tmp:
            color_df.to_csv(tmp, sep=";", index=False)
            colour_path = tmp.name
    except Exception as e:
        st.error(f"Error reading color mapping file: {e}")
        st.stop()

    fig = viz.plot_sankey(
        rdd,
        color_mapping_file=colour_path,
        max_hierarchy_level=max_level or None,
        filename_filter=None if sample_choice == "<all samples>" else sample_choice,
        dark_mode=dark_mode,
    )
    st.plotly_chart(fig, use_container_width=True)

# pages/01_Create_RDD_Count_Table.py
import os, sys, tempfile
import pandas as pd
import streamlit as st
import io

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from src.RDDcounts import RDDCounts  # noqa: E402
from src.state_helpers import set_group  # noqa: E402


# ────────────────────── helpers ──────────────────────
def _read_any(upload):
    ext = os.path.splitext(upload.name)[1].lower()
    sep = "\t" if ext in (".tsv", ".txt") else ","
    return pd.read_csv(upload, sep=sep)


def _persist(upload):
    """Save UploadedFile -> temp file -> path"""
    suf = os.path.splitext(upload.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suf) as tmp:
        tmp.write(upload.getbuffer())
        return tmp.name


# ──────────────── Demo Data Helper ────────────────
def load_demo_file(filename):
    """Load a demo file as a BytesIO object with a name attribute."""
    path = os.path.join(ROOT, "data", filename)
    with open(path, "rb") as f:
        file_obj = io.BytesIO(f.read())
        file_obj.name = filename
        return file_obj


# ────────────────────── UI ──────────────────────
st.header("Create RDD Count Table")

if "use_demo" not in st.session_state:
    st.session_state["use_demo"] = False

if st.button("Use Demo Data"):
    st.session_state["use_demo"] = True

use_demo = st.session_state["use_demo"]

if use_demo:
    gnps_file = load_demo_file("demo_gnps_network.tsv")
    sample_meta_up = None  # Start with None for demo
    ref_meta_up = load_demo_file("foodomics_multiproject_metadata.txt")
    st.info("Demo data loaded. To use your own files, please reload the page.")
else:
    gnps_file = st.file_uploader(
        "GNPS molecular network (.csv / .tsv)", type=("csv", "tsv")
    )
    sample_meta_up = st.file_uploader(
        "Sample metadata (optional)", type=("csv", "tsv", "txt")
    )
    ref_meta_up = st.file_uploader(
        "Reference metadata (optional)", type=("csv", "tsv", "txt")
    )

# -------- discover grouping options --------
sample_group_col = "group"
sample_groups_sel = []

if sample_meta_up:
    meta_df = _read_any(sample_meta_up)
    sample_group_col = st.selectbox(
        "Column to group by",
        meta_df.columns,
        index=list(meta_df.columns).index("group") if "group" in meta_df.columns else 0,
    )
    sample_groups_sel = st.multiselect(
        "Sample groups to include",
        sorted(meta_df[sample_group_col].dropna().unique()),
        default=None,
    )
    reference_groups_sel = None
elif gnps_file:
    gnps_df = _read_any(gnps_file)
    if "DefaultGroups" in gnps_df.columns:
        sample_groups_sel = st.multiselect(
            "Sample groups to include",
            sorted(gnps_df["DefaultGroups"].dropna().unique()),
            default="G1",
        )
        reference_groups_sel = st.multiselect(
            "Reference groups to include",
            sorted(gnps_df["DefaultGroups"].dropna().unique()),
            default="G4",
        )

# -------- other parameters --------
sample_type = st.selectbox("Reference sample type", ("all", "simple", "complex"))
ontology_cols = st.text_input("Custom ontology columns (comma-separated)", "")
levels_val = st.number_input("Maximum ontology levels to analyse", 1, 10, 6, 1)

if ontology_cols and levels_val > len(
    [c for c in ontology_cols.split(",") if c.strip()]
):
    st.warning("Reducing 'levels' to match number of ontology columns.")
    levels_val = len([c for c in ontology_cols.split(",") if c.strip()])

# -------- run --------
if st.button("Generate RDD Counts"):
    if not gnps_file:
        st.error("GNPS file required.")
        st.stop()

    gnps_path = _persist(gnps_file)
    sample_meta_p = _persist(sample_meta_up) if sample_meta_up else None
    ref_meta_p = _persist(ref_meta_up) if ref_meta_up else None
    ontology_list = [c.strip() for c in ontology_cols.split(",") if c.strip()]

    try:
        rdd = RDDCounts(
            gnps_network_path=gnps_path,
            sample_types=sample_type,
            sample_groups=sample_groups_sel or None,
            sample_group_col=sample_group_col,
            levels=levels_val,
            external_reference_metadata=ref_meta_p,
            external_sample_metadata=sample_meta_p,
            ontology_columns=ontology_list or None,
            reference_groups=reference_groups_sel or None,
        )

        # make chosen column the live group
        set_group(rdd, sample_group_col)

        st.session_state["rdd"] = rdd
        st.dataframe(rdd.counts.head(15))
        st.success("RDDCounts object stored in session_state ✅")

        # --- DEMO: Apply demo sample metadata as mapping file ---
        if use_demo:
            demo_mapping = load_demo_file("demo_gnps_metadata.csv")
            mapping_df = pd.read_csv(demo_mapping)
            mapping_df["filename"] = mapping_df["filename"].str.replace(".mzXML", "")
            mapping_df["group"] = mapping_df["group"].str.replace("G1", "Omnivore")
            mapping_df["group"] = mapping_df["group"].str.replace("G2", "Vegan")
            #st.dataframe(mapping_df.head(25))
            if {"filename", "group"}.issubset(mapping_df.columns):
                rdd.counts = rdd.counts.drop("group", axis=1, errors="ignore").merge(
                    mapping_df[["filename", "group"]],
                    left_on="filename", right_on="filename", how="left"
                )
                # --- ADD THIS BLOCK ---
                if "group" in rdd.counts.columns and "filename" in rdd.counts.columns:
                    rdd.sample_metadata = rdd.sample_metadata.drop("group", axis=1, errors="ignore").merge(
                        rdd.counts[["filename", "group"]].drop_duplicates(),
                        on="filename", how="left"
                    )
                # --- END ADD ---
                st.session_state["rdd"] = rdd
                st.success("Demo group assignments applied!")
                st.dataframe(rdd.counts.sample(15))
            else:
                st.warning("Demo sample metadata must have columns: filename, group")

        # --- Allow user to upload a mapping file to change group assignments ---
        st.markdown("### Update Group Assignments")
        mapping_file = st.file_uploader(
            "Upload a mapping file (CSV/TSV: filename,new_group)", type=["csv", "tsv"], key="mapping"
        )

        if mapping_file:
            ext = os.path.splitext(mapping_file.name)[1].lower()
            sep = "\t" if ext in (".tsv", ".txt") else ","
            mapping_df = pd.read_csv(mapping_file, sep=sep)
            if {"filename", "new_group"}.issubset(mapping_df.columns):
                rdd.counts = rdd.counts.merge(
                    mapping_df[["filename", "new_group"]],
                    left_on="filename", right_on="filename", how="left"
                )
                rdd.counts["group"] = rdd.counts["new_group"].combine_first(rdd.counts["group"])
                rdd.counts.drop(columns=["new_group"], inplace=True)
                st.session_state["rdd"] = rdd
                st.success("Group assignments updated!")
                st.dataframe(rdd.counts.head(15))

                # Update sample_metadata with new group assignments
                if "group" in rdd.counts.columns and "filename" in rdd.counts.columns:
                    rdd.sample_metadata = rdd.sample_metadata.drop("group", axis=1, errors="ignore").merge(
                        rdd.counts[["filename", "group"]].drop_duplicates(),
                        on="filename", how="left"
                    )

            else:
                st.error("Mapping file must have columns: filename, new_group")

    except Exception as e:
        st.exception(e)

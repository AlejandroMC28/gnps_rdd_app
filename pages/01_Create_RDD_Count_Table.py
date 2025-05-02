# pages/01_Create_RDD_Count_Table.py
import os, sys, tempfile
import pandas as pd
import streamlit as st

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


# ────────────────────── UI ──────────────────────
st.header("Create RDD Count Table")

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
            default=None,
        )
        reference_groups_sel = st.multiselect(
            "Reference groups to include",
            sorted(gnps_df["DefaultGroups"].dropna().unique()),
            default=None,
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
            reference_groups=reference_groups_sel or None,  # not used
        )

        # make chosen column the live group
        set_group(rdd, sample_group_col)

        st.session_state["rdd"] = rdd
        st.dataframe(rdd.counts.head(15))
        st.success("RDDCounts object stored in session_state ✅")

    except Exception as e:
        st.exception(e)

# ─────────────────────────────────────────────────────────────────────
# visualization.py
#
# • MatplotlibBackend  – static figures
# • PlotlyBackend      – interactive figures (incl. upgraded Sankey)
# • Visualizer         – façade that delegates to the chosen backend
# ─────────────────────────────────────────────────────────────────────

# --- standard -------------------------------------------------------
from collections import defaultdict
from textwrap import shorten
from typing import List, Optional, Tuple
# --- third-party ----------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
# --- internal -------------------------------------------------------
from RDDcounts import RDDCounts
from utils import calculate_proportions
# -------------------------------------------------------------------
#  helpers
# -------------------------------------------------------------------
def _ideal_font_colour(hex_colour: str) -> str:
    """Return 'black' or 'white' for best contrast against hex colour."""
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(2 * c for c in h)
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return "black" if (r * 299 + g * 587 + b * 114) / 1000 > 128 else "white"


def sort_nodes_by_flow(flows_df: pd.DataFrame, processes_df: pd.DataFrame):
    """Heuristic node ordering to reduce Sankey crossings."""
    if "id" not in processes_df.columns:
        uniq = pd.concat([flows_df["source"], flows_df["target"]]).unique()
        processes_df = pd.DataFrame({"id": uniq, "level": 0})
    if "level" not in processes_df.columns:
        processes_df["level"] = 0

    lvl_map = processes_df.set_index("id")["level"].to_dict()
    per_lvl  = defaultdict(list)
    for node, lvl in lvl_map.items():
        per_lvl[lvl].append(node)

    out_sum = flows_df.groupby("source")["value"].sum().to_dict()
    first   = min(per_lvl)
    ordered = {first: sorted(per_lvl[first], key=lambda n: out_sum.get(n, 0), reverse=True)}

    for lvl in range(first + 1, max(per_lvl) + 1):
        if lvl not in per_lvl:
            continue
        prev = ordered[lvl - 1]
        cur  = per_lvl[lvl]
        conn = defaultdict(list)
        for s, t, v in flows_df[["source", "target", "value"]].values:
            if s in prev and t in cur:
                conn[s].append((t, v))
        cur_sorted = []
        for p in prev:
            cur_sorted += [t for t, _ in sorted(conn[p], key=lambda x: x[1], reverse=True)]
        cur_sorted += list(set(cur) - set(cur_sorted))
        ordered[lvl] = cur_sorted

    nodes = [n for lvl in sorted(ordered) for n in ordered[lvl]]
    idx   = {n: i for i, n in enumerate(nodes)}
    return nodes, idx
# -------------------------------------------------------------------
#  data preparation helpers
# -------------------------------------------------------------------
def filter_and_group_RDD_counts(rdd: RDDCounts, level: int,
                                reference_types: Optional[List[str]] = None,
                                group_by: bool = False) -> pd.DataFrame:
    df = rdd.filter_counts(reference_types, level)
    if df.empty:
        raise ValueError("No data for selected level/reference types.")
    if group_by:
        df = df.groupby(["reference_type", "group"])["count"].sum().reset_index()
    else:
        df = df.groupby("reference_type")["count"].sum().reset_index()
    return df


def prepare_boxplot_data(rdd: RDDCounts, level: int,
                         reference_types: Optional[List[str]] = None) -> pd.DataFrame:
    props = calculate_proportions(rdd.counts, level)
    long  = props.reset_index().melt(id_vars=["filename", "group"],
                                     var_name="reference_type",
                                     value_name="proportion")
    if reference_types:
        long = long[long["reference_type"].isin(reference_types)]
    if long.empty:
        raise ValueError("No data for selected reference types.")
    return long


def prepare_heatmap_data(rdd: RDDCounts, level: int,
                         reference_types: Optional[List[str]] = None) -> pd.DataFrame:
    props = calculate_proportions(rdd.counts, level)
    if reference_types:
        props = props[props.columns.intersection(reference_types)]
    return props.select_dtypes(include=["int", "float"])
# -------------------------------------------------------------------
#  abstract backend
# -------------------------------------------------------------------
from abc import ABC, abstractmethod

class VisualizationBackend(ABC):
    @abstractmethod
    def plot_reference_type_distribution(self, data, group_by, figsize, **kw): ...
    @abstractmethod
    def box_plot_RDD_proportions(self, data, group_by=False, group_colors=None, figsize=(10, 6), **kw): ...
    @abstractmethod
    def plot_RDD_proportion_heatmap(self, data, level, figsize, **kw): ...
    @abstractmethod
    def plot_pca_results(self, pca_df, explained, x_pc, y_pc, group_by, group_colors, figsize, **kw): ...
    @abstractmethod
    def plot_explained_variance(self, explained, figsize, **kw): ...
    @abstractmethod
    def plot_sankey(self, rdd: RDDCounts, color_map_file, max_level, filename_filter, dark_mode) -> go.Figure: ...
# -------------------------------------------------------------------
#  Matplotlib backend  (unchanged versus earlier)
# -------------------------------------------------------------------
class MatplotlibBackend(VisualizationBackend):
    def plot_reference_type_distribution(self, data, group_by, figsize, **kw):
        fig, ax = plt.subplots(figsize=figsize)
        if group_by:
            sns.barplot(x="reference_type", y="count", hue="group", data=data, ax=ax)
        else:
            sns.barplot(x="reference_type", y="count", data=data, hue="reference_type", ax=ax, legend=False)
        ax.set_xlabel("Reference type"); ax.set_ylabel("Total count"); plt.xticks(rotation=45, ha="right")
        return fig

    def box_plot_RDD_proportions(self, data, group_by=False, group_colors=None, figsize=(10, 6), **kw):
        fig, ax = plt.subplots(figsize=figsize)
        if group_by:
            sns.boxplot(x="reference_type", y="proportion", hue="group", data=data, ax=ax, palette=group_colors)
        else:
            sns.boxplot(x="reference_type", y="proportion", data=data, hue="reference_type", ax=ax, legend=False)
        ax.set_xlabel("Reference type"); ax.set_ylabel("Proportion"); plt.xticks(rotation=45, ha="right")
        return fig

    def plot_RDD_proportion_heatmap(self, data, level, figsize, **kw):
        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(data, cmap="viridis", ax=ax, cbar=True, **kw)
        ax.set_xlabel("Reference type"); ax.set_ylabel("Sample")
        return fig

    def plot_pca_results(
        self,
        pca_df: pd.DataFrame,
        explained_variance: List[float],
        x_pc: str = "PC1",                  # ← default
        y_pc: str = "PC2",                  # ← default
        group_by: bool = True,
        group_colors: Optional[dict] = None,
        figsize: Tuple[int, int] = (10, 6), # ← default
        group_column: str = "group",
        **kwargs,
    ):
        fig, ax = plt.subplots(figsize=figsize)
        if group_by:
            sns.scatterplot(x=x_pc, y=y_pc, hue="group", data=pca_df, ax=ax, palette=group_colors)
        else:
            sns.scatterplot(x=x_pc, y=y_pc, data=pca_df, ax=ax)
        ax.set_xlabel(f"{x_pc} ({explained_variance[int(x_pc[2])-1]*100:.1f}%)")
        ax.set_ylabel(f"{y_pc} ({explained_variance[int(y_pc[2])-1]*100:.1f}%)")
        return fig

    def plot_explained_variance(self, explained_variance, figsize: Tuple[int, int] = (10, 6),
                                **kwargs,):
        labels = [f"PC{i+1}" for i in range(len(explained_variance))]
        perc   = [v*100 for v in explained_variance]
        fig, ax = plt.subplots(figsize=figsize)
        sns.barplot(x=labels, y=perc, ax=ax, color="blue")
        for i, v in enumerate(perc): ax.text(i, v + 1, f"{v:.1f}%", ha="center")
        ax.set_ylabel("Explained variance (%)"); ax.set_xlabel("PC")
        return fig

    def plot_sankey(self, *_, **__):
        raise NotImplementedError("Matplotlib backend does not support Sankey")
# -------------------------------------------------------------------
#  Plotly backend  (includes new Sankey)
# -------------------------------------------------------------------
class PlotlyBackend(VisualizationBackend):
    # -- bar ---------------------------------------------------------
    def plot_reference_type_distribution(self, data, group_by, figsize, **kw):
        fig = px.bar(data, x="reference_type", y="count",
                     color="group" if group_by else None,
                     barmode="group" if group_by else "relative", **kw)
        fig.update_layout(xaxis_title="Reference type", yaxis_title="Total count", template="plotly_white")
        return fig
    # -- box ---------------------------------------------------------
    def box_plot_RDD_proportions(
    self,
    data: pd.DataFrame,
    group_by: bool = False,
    group_colors: Optional[dict] = None,
    figsize: Tuple[int, int] = (10, 6),   # ← added
    **kw,
):
        fig = go.Figure()
        if group_by:
            for g in data["group"].unique():
                gd = data[data["group"] == g]
                fig.add_trace(
                    go.Box(
                        x=gd["reference_type"],
                        y=gd["proportion"],
                        name=g,
                        boxpoints="all",
                        jitter=0.3,
                        pointpos=0,
                        marker_color=(group_colors or {}).get(g),
                    )
                )
        else:
            for rt in data["reference_type"].unique():
                rd = data[data["reference_type"] == rt]
                fig.add_trace(
                    go.Box(
                        x=rd["reference_type"],
                        y=rd["proportion"],
                        name=rt,
                        boxpoints="all",
                        jitter=0.3,
                        pointpos=0,
                    )
                )
        fig.update_layout(
            xaxis_title="Reference type",
            yaxis_title="Proportion",
            boxmode="group" if group_by else "overlay",
        )
        return fig

    # -- heatmap -----------------------------------------------------
    def plot_RDD_proportion_heatmap(self, data, level, figsize, **kw):
        fig = go.Figure(go.Heatmap(z=data.values, x=data.columns, y=data.index,
                                   colorscale="Viridis", colorbar_title="Proportion"))
        fig.update_layout(title=f"Heatmap (level {level})",
                          xaxis_title="Reference type", yaxis_title="Sample",
                          template="plotly_white")
        return fig
    # -- PCA scatter -------------------------------------------------
    def plot_pca_results(
    self,
    pca_df: pd.DataFrame,
    explained_variance: List[float],
    x_pc: str = "PC1",               # ← default
    y_pc: str = "PC2",               # ← default
    group_by: bool = True,
    group_colors: Optional[dict] = None,
    figsize: Tuple[int, int] = (10, 6),   # ← default
    group_column: str = "group",     # ← accepts wrapper arg
    **kw,
):
        """Scatter-plot of PCA scores (Plotly)."""
        fig = px.scatter(
            pca_df,
            x=x_pc,
            y=y_pc,
            color=group_column if group_by else None,
            color_discrete_map=group_colors,
            **kw,
        )
        fig.update_layout(
            xaxis_title=f"{x_pc} ({explained_variance[int(x_pc[2]) - 1]*100:.1f}%)",
            yaxis_title=f"{y_pc} ({explained_variance[int(y_pc[2]) - 1]*100:.1f}%)",
            template="plotly_white",
        )
        return fig
    # -- explained variance -----------------------------------------
    def plot_explained_variance(self, explained_variance, figsize: Tuple[int, int] = (10, 6), **kw):
        labels = [f"PC{i+1}" for i in range(len(explained_variance))]
        perc   = [v*100 for v in explained_variance]
        fig = go.Figure(go.Bar(x=labels, y=perc, text=[f"{p:.1f}%" for p in perc],
                               textposition="auto"))
        fig.update_layout(xaxis_title="PC", yaxis_title="Explained variance (%)",
                          template="plotly_white")
        return fig
    # -- Sankey ------------------------------------------------------

    # ────────────────────────────────────────────────────────────────
    #  Sankey
    # ────────────────────────────────────────────────────────────────
    def plot_sankey(
        self,
        RDD_counts: "RDDCounts",
        color_mapping_file: Optional[str] = None,      # optional palette
        max_hierarchy_level: Optional[int] = None,
        filename_filter: Optional[str] = None,
        dark_mode: bool = False,
        *,
        per_level_scale: bool = True,                  # NEW: scale each level
        log_scale: bool = False,                       # keep old option
        max_px: int = 20,                              # max link thickness
        max_label_len: int = 18,
    ) -> go.Figure:
        """
        Draw an RDD Sankey diagram.

        - If *color_mapping_file* is **None** the diagram falls back to a
          greyscale palette that works in both light and dark themes.
        - If *per_level_scale* is **True** every source-level is scaled
          independently so top-level flows are always thicker than deeper ones.
        """

        # ---- 1.  build flow table ---------------------------------
        flows_df, processes_df = RDD_counts.generate_RDDflows(
            max_hierarchy_level=max_hierarchy_level,
            filename_filter=filename_filter,
        )
        sorted_nodes, node_idx = sort_nodes_by_flow(flows_df, processes_df)

        # map to integer indices expected by Plotly
        src = flows_df["source"].map(node_idx)
        tgt = flows_df["target"].map(node_idx)

        # ---- 2.  link thickness -----------------------------------
        if per_level_scale:
            # split “plant_1”, “fruit_2”, … into (name, level)
            flows_df["src_lvl"] = flows_df["source"].str.rsplit("_", n=1).str[-1].astype(int)
            lvl_max = flows_df.groupby("src_lvl")["value"].transform("max")
            link_val = max_px * flows_df["value"] / lvl_max
        elif log_scale:
            link_val = max_px * np.log10(flows_df["value"] + 1) / np.log10(flows_df["value"].max() + 1)
        else:
            link_val = max_px * flows_df["value"] / flows_df["value"].max()

        # ---- 3.  colour mapping -----------------------------------
        NODE_GREY = "#D3D3D3"
        LINK_GREY = "rgba(211,211,211,0.4)"
        colour_map: dict[str, str] = {}

        if color_mapping_file:
            cm_df = pd.read_csv(color_mapping_file, sep=";")
            cm_df["color_code"] = cm_df["color_code"].fillna(NODE_GREY)
            colour_map = dict(zip(cm_df["descriptor"], cm_df["color_code"]))

        node_colors = [colour_map.get(n.split("_")[0], NODE_GREY) for n in sorted_nodes]
        link_colors = [colour_map.get(s.split("_")[0], LINK_GREY) for s in flows_df["source"]]

        # ---- 4.  figure -------------------------------------------
        labels = [shorten(n.split("_")[0], width=max_label_len, placeholder="…")
                  if max_label_len else n.split("_")[0] for n in sorted_nodes]

        fig = go.Figure(
            go.Sankey(
                arrangement="snap",
                node=dict(pad=15, thickness=20, line=dict(width=0.5, color="black"),
                          label=labels, color=node_colors),
                link=dict(source=src, target=tgt, value=link_val, color=link_colors),
            )
        )

        # ---- 5.  styling ------------------------------------------
        fig.update_traces(textfont=dict(size=14, color="white" if dark_mode else "black"))

        if dark_mode:
            fig.update_layout(title_text="RDD Flows Sankey Diagram",
                              font_color="white",
                              paper_bgcolor="black",
                              plot_bgcolor="black")
        else:
            fig.update_layout(title_text="RDD Flows Sankey Diagram",
                              template="plotly_white")

        return fig

    

# -------------------------------------------------------------------
#  Visualizer façade
# -------------------------------------------------------------------
class Visualizer:
    """Front-end class that delegates to a chosen backend instance."""
    def __init__(self, backend: VisualizationBackend):
        self.backend = backend

    def set_backend(self, backend: VisualizationBackend):
        self.backend = backend

    # ---- wrappers --------------------------------------------------
    def plot_reference_type_distribution(self, rdd, level=3, reference_types=None,
                                         group_by=False, figsize=(10, 6), **kw):
        data = filter_and_group_RDD_counts(rdd, level, reference_types, group_by)
        return self.backend.plot_reference_type_distribution(data, group_by, figsize, **kw)

    def box_plot_RDD_proportions(self, rdd, level=3, reference_types=None,
                                 group_by=False, group_colors=None, figsize=(10, 6), **kw):
        data = prepare_boxplot_data(rdd, level, reference_types)
        return self.backend.box_plot_RDD_proportions(data, group_by, group_colors, figsize, **kw)

    def plot_RDD_proportion_heatmap(self, rdd, level=3, reference_types=None,
                                    figsize=(12, 8), **kw):
        data = prepare_heatmap_data(rdd, level, reference_types)
        return self.backend.plot_RDD_proportion_heatmap(data, level, figsize, **kw)

    def plot_pca_results(self, *a, **k):
        return self.backend.plot_pca_results(*a, **k)

    def plot_explained_variance(self, *a, **k):
        return self.backend.plot_explained_variance(*a, **k)

    def plot_sankey(self, *a, **k):
        return self.backend.plot_sankey(*a, **k)

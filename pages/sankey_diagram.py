import streamlit as st
from streamlit_navigation_bar import st_navbar
import pandas as pd
import numpy as np
import os
import math
import plotly.graph_objects as go

st.set_page_config(initial_sidebar_state="auto")

page = st_navbar(["Home", "Create Food Counts", "Visualization", "PCA", "Sankey Diagram", "How to use"], selected="Sankey Diagram")

if page == "Create Food Counts":
    st.switch_page("pages/create_food_counts.py")
if page == "Visualization":
    st.switch_page("pages/dynamic_filtering_visualization.py")
if page == "Home":
    st.switch_page("home.py")
if page == "PCA":
    st.switch_page("pages/PCA.py")
if page == "How to use":
    st.switch_page("pages/how_to_use.py")

def load_food_metadata() -> pd.DataFrame:
    stream = os.path.join(os.path.dirname(__file__), '..', 'data', 'foodomics_multiproject_metadata.txt')
    gfop_metadata = pd.read_csv(stream, sep="\t")
    gfop_metadata = gfop_metadata.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return gfop_metadata

def get_sample_types_flows(simple_complex='all'):
    gfop_metadata = load_food_metadata()
    if simple_complex != 'all':
        gfop_metadata = gfop_metadata[gfop_metadata['simple_complex'] == simple_complex]
    col_sample_types = ['sample_name'] + [f'sample_type_group{i}' for i in range(1, 7)]
    return gfop_metadata[['filename', *col_sample_types]].set_index('filename')

def _get_flows(gnps_network, sample_types, groups_included, max_hierarchy_level):
    groups = {f'G{i}' for i in range(1, 7)}
    groups_excluded = list(groups - set(groups_included))
    df_selected = gnps_network[
        (gnps_network[groups_included] > 0).all(axis=1) &
        (gnps_network[groups_excluded] == 0).all(axis=1)].copy()
    filenames = df_selected['UniqueFileSources'].str.split('|').explode()
    sample_types = sample_types[[f'sample_type_group{i}' for i in range(1, max_hierarchy_level + 1)]]
    sample_types_selected = sample_types.reindex(filenames).dropna()
    water_count = ((sample_types_selected['sample_type_group1'] == 'water').sum())
    sample_counts = sample_types_selected[f'sample_type_group{max_hierarchy_level}'].value_counts()
    sample_counts_valid = sample_counts.index[sample_counts > water_count]
    sample_types_selected = sample_types_selected[sample_types_selected[f'sample_type_group{max_hierarchy_level}'].isin(sample_counts_valid)]
    flows, processes = [], []
    for i in range(1, max_hierarchy_level):
        g1, g2 = f'sample_type_group{i}', f'sample_type_group{i + 1}'
        flow = (sample_types_selected.groupby([g1, g2]).size()
                .reset_index().rename(columns={g1: 'source', g2: 'target', 0: 'value'}))
        flow['source'] = flow['source'] + f'_{i}'
        flow['target'] = flow['target'] + f'_{i + 1}'
        flow['type'] = flow['target']
        flows.append(flow)
        process = pd.concat([flow['source'], flow['target']],
                            ignore_index=True).to_frame()
        process['level'] = [*np.repeat(i, len(flow['source'])),
                            *np.repeat(i + 1, len(flow['target']))]
        processes.append(process)
    return pd.concat(flows, ignore_index=True), pd.concat(processes, ignore_index=True).drop_duplicates().rename(columns={0: 'id'}).set_index('id')

st.title("Sankey Diagram")

st.write("""
A Sankey diagram is a visualization tool that shows the flow of data between different stages or categories. 
On this page, you can create a Sankey diagram to visualize the flow of food items through different hierarchical levels, 
providing insights into the composition and distribution of your foodomics data.
""")

st.sidebar.header("Settings")

simple_complex_flows = st.sidebar.selectbox(
    "Select Food Type for flow visualization", ["all", "simple", "complex"],
    help="Choose whether to include simple, complex, or all food types in the flow visualization."
)

groups_for_flows = st.sidebar.multiselect(
    "Select Groups for flow visualization", [f'G{i}' for i in range(1, 7)], ['G1', 'G4'],
    help="Select the groups you want to include in the flow visualization."
)

max_hierarchy_flows = st.sidebar.slider(
    "Select Max Hierarchy Level", 0, 6, 4,
    help="Choose the maximum hierarchy level to be included in the Sankey diagram. Higher levels provide more detailed categorization."
)



gnps_network_file = st.file_uploader(
    "Upload your molecular network file", type=["csv", "tsv"],
    help="Upload your GNPS molecular network file to generate the Sankey diagram."
)

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

use_demo = st.sidebar.checkbox("Use Demo Data")

if use_demo:
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    gnps_df = pd.read_csv(os.path.join(data_dir, 'demo_gnps_network.tsv'), sep='\t')

if gnps_network_file or use_demo:
    st.write("""
    After uploading the necessary files, the Sankey diagram will be generated, showing the flow of food items through the selected hierarchical levels.
    This visualization helps you understand the distribution and composition of food samples across different categories.
    """)
    if gnps_network_file:
        gnps_network = pd.read_csv(gnps_network_file, sep='\t')
    elif use_demo:
        gnps_network = gnps_df
    #sample_type_hierarchy = pd.read_csv(hierarchical_levels_file, delimiter=';').set_index('descriptor').sort_values('order_num')
    sample_type_hierarchy = pd.read_csv(os.path.join(data_dir, 'sample_type_hierarchy.csv'),delimiter=';').set_index('descriptor').sort_values('order_num')

    sample_types_flows = get_sample_types_flows(simple_complex_flows)
    flows, procs = _get_flows(gnps_network, sample_types_flows, groups_for_flows, max_hierarchy_flows)

    id_to_level = dict(zip(procs.index, procs['level']))

    nodes = list(set(flows['source']).union(set(flows['target'])))
    node_indices = {node: idx for idx, node in enumerate(nodes)}

    sources = [node_indices[src] for src in flows['source']]
    targets = [node_indices[tgt] for tgt in flows['target']]

    # Sort nodes by level to reduce crossings
    sorted_nodes = sorted(nodes, key=lambda x: id_to_level.get(x, float('inf')))
    sorted_node_indices = {node: idx for idx, node in enumerate(sorted_nodes)}

    # Recalculate sources and targets based on the sorted nodes
    sorted_sources = [sorted_node_indices[src] for src in flows['source']]
    sorted_targets = [sorted_node_indices[tgt] for tgt in flows['target']]

    values = flows['value']

    width = max_hierarchy_flows * 150 + 300
    height = math.ceil(sum([1 for node in nodes if id_to_level.get(node, 0) == max_hierarchy_flows]) * 50 / 100) * 100



     # Map colors from the sample_type_hierarchy to the nodes
    descriptor_to_color = sample_type_hierarchy['color_code'].to_dict()

    descriptor_to_color = {k: v if pd.notna(v) else '#CCCCCC' for k, v in descriptor_to_color.items()}

    # Apply colors to nodes and links
    node_colors = [descriptor_to_color.get(node, '#CCCCCC') for node in sorted_nodes]
    link_colors = [descriptor_to_color.get(node, '#CCCCCC') for node in flows['source']]

    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=sorted_nodes,
            color=node_colors
        ),
        link=dict(
            source=sorted_sources,
            target=sorted_targets,
            value=values,
            color=link_colors
        ),
        textfont=dict(
        color='black',
        size=15,
        family='Arial black'  # Use a bold font family
    )
    )])

    fig.update_layout(
        title_text="Sankey Diagram",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_size=15,
        width=width,
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),  # Adjusted margins
        font=dict(
            size=20,  # Adjust this value to make the font larger or smaller
            color="Black"  # Change the font color if needed
        )
    )

    # Display the Sankey diagram in Streamlit
    st.plotly_chart(fig)

    st.write("""
    The Sankey diagram above represents the flow of food items through the selected hierarchical levels. 
    Each node represents a category at a specific level, and the links between nodes show the flow of items from one level to the next.
    The thickness of each link corresponds to the quantity of items flowing between categories.
    """)

else:
    st.write("""
    Please upload the GNPS molecular network file to generate the Sankey diagram.
    """)

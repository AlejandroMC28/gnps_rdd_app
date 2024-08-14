import streamlit as st
import pandas as pd
import os
from src.data_processing import load_food_metadata, get_sample_metadata, get_sample_types, get_dataset_food_counts_all
from streamlit_navigation_bar import st_navbar


st.set_page_config(initial_sidebar_state="auto")

page = st_navbar(["Home", "Create Food Counts", "Visualization", "PCA", "Sankey Diagram"], selected= 'Create Food Counts')

if page == "PCA":
    st.switch_page("pages/PCA.py")
if page == "Visualization":
    st.switch_page("pages/dynamic_filtering_visualization.py")
if page == "Home":
    st.switch_page("home.py")
if page == "Sankey Diagram":
    st.switch_page("pages/sankey_diagram.py")





st.title("Generate Food Counts")

st.sidebar.header("Settings")
all_groups = st.sidebar.multiselect("Select all groups (e.g., G1, G2)", options=['G1', 'G2', 'G5', 'G6'], default=['G1'])
some_groups = st.sidebar.multiselect("Select some groups (e.g., G3, G4)", options=['G3', 'G4'], default=['G4'])
simple_complex = st.sidebar.selectbox("Select food type", ['all', 'simple', 'complex'])

use_demo = st.sidebar.checkbox("Use Demo Data")

if use_demo:
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    gnps_df = pd.read_csv(os.path.join(data_dir, 'demo_gnps_network.tsv'), sep='\t')
    st.session_state.gnps_df = gnps_df
    st.write("Using demo GNPS network data:")
    st.write(gnps_df.head())
else:
    uploaded_file = st.file_uploader("Upload your molecular network file", type=["csv", "tsv"])
    if uploaded_file is not None:
        gnps_df = pd.read_csv(uploaded_file, sep='\t' if uploaded_file.name.endswith('.tsv') else ',')
        st.session_state.gnps_df = gnps_df
        st.write("Uploaded GNPS network data:")
        st.write(gnps_df.head())

if 'gnps_df' in st.session_state:
    if st.button("Generate Food Counts"):
        food_counts = get_dataset_food_counts_all(st.session_state.gnps_df, simple_complex, all_groups, some_groups)
        st.session_state.food_counts = food_counts
        st.write('Generated food counts:')
        st.write(food_counts.head())
        st.session_state.food_counts_generated = True

if 'food_counts_generated' in st.session_state and st.session_state.food_counts_generated:
    st.write("Food counts have been generated. You can now use other metadata.")


    sample_file = st.file_uploader('Upload food metadata', type=["csv", "tsv"])
    if sample_file is not None:
        sample_metadata = pd.read_csv(sample_file, sep='\t' if sample_file.name.endswith('.tsv') else ',')
        st.session_state.sample_metadata = sample_metadata
        st.write("Uploaded sample metadata:")
        st.write(sample_metadata.head())

    if 'sample_metadata' in st.session_state and use_demo == False:
        new_group_column = st.selectbox('Select new group column', st.session_state.sample_metadata.columns)
        st.write(f"Selected new group column: {new_group_column}")
        
        if st.button("Join and Replace Group"):
            combined_df = st.session_state.food_counts.merge(st.session_state.sample_metadata[['filename', new_group_column]], on='filename', how='left')
            
            if 'group' in combined_df.columns:
                combined_df['group'] = combined_df[new_group_column]
            else:
                combined_df['group'] = combined_df[new_group_column]
            
            combined_df = combined_df.drop(columns=[new_group_column])
            
            st.session_state.food_counts = combined_df
            st.write('Group has been changed successfully:')
            st.write(combined_df.head())
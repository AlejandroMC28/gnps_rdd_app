import streamlit as st
from streamlit_navigation_bar import st_navbar

st.set_page_config(initial_sidebar_state="collapsed", page_icon="🍋")

page = st_navbar(["Home", "Create count table", "Visualization", "PCA", "Sankey Diagram", "How to use"], selected= 'Home')

if page == "Create count table":
    st.switch_page("pages/create_food_counts.py")
if page == "Visualization":
    st.switch_page("pages/dynamic_filtering_visualization.py")
if page == "PCA":
    st.switch_page("pages/PCA.py")
if page == "Sankey Diagram":
    st.switch_page("pages/sankey_diagram.py")
if page == "How to use":
    st.switch_page("pages/how_to_use.py")

app_path = 'https://gnps-rdd.streamlit.app/'
page_file_path = 'pages/'
page = page_file_path.split('/')[1][0:-3]  # get "home"

# Title and Introduction
st.title("Welcome to the Reference Data Driven Metabolomics Application")
st.write("""
This application is designed to help you gain powerful insights from your metabolomics data by leveraging **Reference Data-Driven (RDD) metabolomics**. 
RDD enhances the interpretability of untargeted metabolomics by integrating curated reference datasets with detailed metadata, allowing for more contextual and meaningful analysis.
""")

# About the Foodomics Dataset
st.header("Choosing a Reference Dataset")
st.subheader("Global Foodomics")
st.write("""
The Foodomics dataset is a comprehensive collection of over **3,000 food items**, organized into a detailed **seven-level ontology**. This dataset, which includes rich metadata on the geographical origin, processing methods, and dietary sources, 
is foundational to the insights you can gain from this application. By exploring this dataset, you can delve into various food samples and human biospecimens, identifying complex relationships and dietary patterns.

**We invite you to collaborate in expanding this dataset.** Contributions from diverse sources, including new data are welcome. Together, we can enhance our understanding and broaden the scope of this project.
""")

# Using the Application
st.header("Using the Application")
st.markdown(f"""
This tool allows you to:
- Generate detailed food counts linked to metadata.
- Explore and visualize your data through interactive charts and graphs.
- Perform advanced analyses such as Principal Component Analysis (PCA) and Sankey diagram creation.

For a detailed guide on how to use the app, including step-by-step instructions and example workflows, please visit our <a href="{app_path}/{page}" target="_self">How to Use</a>
tab. 
This section provides everything you need to get started, as well as links to additional resources.
""", unsafe_allow_html=True)

# Citing This Tool
st.header("Citing This Tool")
st.write("""
When using this tool in your research, please cite the following paper:


This app is provided under **[specific license type]**, and we ask that you adhere to the licensing terms when using the data and features provided.
""")






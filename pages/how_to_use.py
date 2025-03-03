import streamlit as st
from streamlit_navigation_bar import st_navbar

st.set_page_config(initial_sidebar_state="collapsed")

page = st_navbar(["Home", "Create count table", "Visualization", "PCA", "Sankey Diagram", "How to use"], selected= "How to use")

if page == "PCA":
    st.switch_page("pages/PCA.py")
if page == "Create count table":
    st.switch_page("pages/create_food_counts.py")
if page == "Home":
    st.switch_page("home.py")
if page == "Sankey Diagram":
    st.switch_page("pages/sankey_diagram.py")
if page == "Visualization":
    st.switch_page("pages/dynamic_filtering_visualization.py")


st.title("How to Use")

# Section 1: Generate Food Counts
st.header("1. Generate Food Counts")
st.markdown("""
- **Navigate to the "Create Food Counts" page.**
- **Data Upload**: Upload your GNPS job result file in CSV or TSV format using the file uploader.
- **Select Sample Groups**: Use the multiselect dropdowns in the sidebar to select the sample groups in your data (e.g., G1, G2 for study groups, and G3, G4 for reference groups).
- **Choose Food Type**: Select whether the reference sample type is 'simple', 'complex', or 'all' using the dropdown in the sidebar.
- **Generate**: Click the "Generate Food Counts" button to process the data and generate the food counts table. A message will confirm when the food counts are generated successfully.
- **Optional - Upload Metadata**: You can also upload a sample metadata file in CSV or TSV format. Once uploaded, you can join it with the food counts by selecting a new group column from the dropdown and clicking the "Join and Replace Group" button.
""")

# Section 2: Filter and Visualize Food Counts
st.header("2. Filter and Visualize Food Counts")
st.markdown("""
- **Navigate to the "Dynamic Filtering and Visualization" page.**
- **Select Hierarchy Level**: Use the slider in the sidebar to select the hierarchy level of the food data you want to visualize.
- **Filter Data**: Use the multiselect dropdown to choose the columns you want to display in the table.
- **Rename Groups**: Optionally, rename group values by entering new names in the provided text inputs.
- **Select Plot Type**: Choose the type of plot for visualization (Bar Plot, Box Plot, Heatmap, or Clustered Heatmap) from the dropdown.
- **Group By Option**: Optionally, check the box to group data by the 'group' column.
- The filtered data and selected visualizations will be displayed on the main page.
""")

# Section 3: PCA Analysis
st.header("3. PCA Analysis")
st.markdown("""
- **Navigate to the "PCA Analysis" page.**
- **Select Hierarchy Level**: Choose the hierarchy level for the PCA from the dropdown in the sidebar.
- **Rename Groups**: Optionally, rename group values using the provided text inputs.
- **Select Features**: Use the multiselect dropdown to select features for the PCA analysis.
- **Choose Components**: Use the slider to select the number of principal components for the analysis.
- **Apply CLR Transformation**: Optionally, check the box to apply CLR (Centered Log Ratio) transformation and set the offset value.
- The PCA results, including the variance explained by each component and a scatter plot of the principal components, will be displayed.
""")

# Section 4: Sankey Diagram
st.header("4. Sankey Diagram")
st.markdown("""
- **Navigate to the "Sankey Diagram" page.**
- **Select Food Type**: Choose the type of food data for flow visualization (simple, complex, or all) from the dropdown in the sidebar.
- **Select Groups and Hierarchy Level**: Use the multiselect dropdown to select the groups and the slider to select the maximum hierarchy level for visualization.
- **Upload Files**: Upload the hierarchy file and the molecular network file using the file uploaders.
- The Sankey diagram will be generated and displayed based on the uploaded data and selected settings.
""")

st.write("Follow these steps to explore the foodomics data and create your insights.")

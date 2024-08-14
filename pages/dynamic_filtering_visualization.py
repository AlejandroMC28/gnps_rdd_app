import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.visualization import bar_plot_food_counts, box_plot_food_proportions, transform_to_proportions, show_heatmap
from streamlit_navigation_bar import st_navbar

st.set_page_config(initial_sidebar_state="auto")

page = st_navbar(["Home", "Create Food Counts", "Visualization", "PCA", "Sankey Diagram", "How to use"], selected= 'Visualization')

if page == "PCA":
    st.switch_page("pages/PCA.py")
if page == "Create Food Counts":
    st.switch_page("pages/create_food_counts.py")
if page == "Home":
    st.switch_page("home.py")
if page == "Sankey Diagram":
    st.switch_page("pages/sankey_diagram.py")
if page == "How to use":
    st.switch_page("pages/how_to_use.py")

st.title("Dynamic Filtering and Visualization")

st.write("""
On this page, you can filter your food counts data dynamically and create visualizations to explore patterns and insights within your dataset. 
Use the sidebar to customize your filtering options and choose how you'd like to visualize the data.
""")

st.sidebar.header("Dynamic Filtering Settings")

level = st.sidebar.slider(
    "Select hierarchy level",
    0, 6, 3,
    help="Select the hierarchy level of the food data, with higher levels providing more specific categories."
)

if 'food_counts_generated' in st.session_state and st.session_state.food_counts_generated:
    if 'food_counts' in st.session_state:
        food_counts = st.session_state.food_counts[st.session_state.food_counts['level'] == level]
        food_counts = food_counts.pivot_table(index='filename', columns='food_type', values='count', fill_value=0)
        group_df = st.session_state.food_counts[['filename', 'group']].drop_duplicates().set_index('filename')
        food_counts = food_counts.join(group_df)

        st.subheader('Rename Group Values')
        st.write("""
        You can rename group values to better reflect the categories in your analysis. 
        This is useful for tailoring the output to your specific needs or making it more intuitive for others who may view your results.
        """)
        
        group_values = food_counts['group'].unique()
        new_group_names = {}
        
        for value in group_values:
            new_name = st.text_input(f'New name for {value}', value)
            new_group_names[value] = new_name
        
        food_counts['group'] =  food_counts['group'].map(new_group_names)

        st.write("### Food Counts by Level")
        st.write("""
        Select the columns you want to display from your filtered food counts. 
        Once you've selected the columns, choose a visualization type to better understand your data.
        """)

        columns = food_counts.columns.tolist()
        columns.remove('group')
        selected_columns = st.multiselect("Select columns to display", columns, default=columns)

        selected_columns.append('group')

        filtered_food_counts = food_counts[selected_columns]
        st.dataframe(filtered_food_counts)

        st.write("### Visualization")
        plot_type = st.selectbox("Select plot type", ["Bar Plot", "Box Plot", "Heatmap"])
        group_by = st.checkbox("Group by 'group' column")
        
        if plot_type == "Bar Plot":
            st.write("#### Bar Plot")
            bar_plot_food_counts(filtered_food_counts, group_by)

        elif plot_type == "Box Plot":
            st.write("#### Box Plot")
            selected_columns_boxplot = st.multiselect("Select columns to display", columns, None)
            selected_columns_boxplot.append('group')
            box_plot_food_proportions(food_counts[selected_columns_boxplot], group_by)

        elif plot_type == "Heatmap":
            st.write("#### Heatmap")
            clustering = st.checkbox('Clustering')
            heatmap_df = transform_to_proportions(filtered_food_counts)
            show_heatmap(heatmap_df, apply_clustering=clustering)

else:
    st.warning("Please generate food counts first by navigating to the 'Create Food Counts' tab. You'll need to generate counts before you can filter or visualize the data.")

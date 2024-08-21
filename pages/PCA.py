import streamlit as st
from streamlit_navigation_bar import st_navbar
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

st.set_page_config(initial_sidebar_state="auto")

page = st_navbar(["Home", "Create Food Counts", "Visualization", "PCA", "Sankey Diagram", "How to use"], selected='PCA')

if page == "Create Food Counts":
    st.switch_page("pages/create_food_counts.py")
if page == "Visualization":
    st.switch_page("pages/dynamic_filtering_visualization.py")
if page == "Home":
    st.switch_page("home.py")
if page == "Sankey Diagram":
    st.switch_page("pages/sankey_diagram.py")
if page == "How to use":
    st.switch_page("pages/how_to_use.py")


def run_pca(data, features, n_components, apply_clr=False, offset=1):
    """Performs PCA on the provided data."""
    if apply_clr:
        transformed_data = clr_transformation(data[features], offset=offset)
        st.write(transformed_data)
    else:
        transformed_data = data[features]
        
    scaled_data = StandardScaler().fit_transform(transformed_data)
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(scaled_data)
    
    explained_variance = pca.explained_variance_ratio_
    explained_variance_df = pd.DataFrame({
        'PC': [f'PC{i+1}' for i in range(n_components)],
        'Explained Variance': explained_variance
    })

    pca_columns = [f'PC{i+1}' for i in range(n_components)]
    pca_df = pd.DataFrame(data=pca_result, columns=pca_columns)
    pca_df = pd.concat([pca_df, data.reset_index(drop=True)], axis=1)
    
    return pca_df, explained_variance_df, pca_columns


def clr_transformation(data, offset=1):
    """Applies Centered Log Ratio (CLR) transformation with an offset."""
    data = data + offset
    log_data = np.log(data)
    clr_data = log_data - log_data.mean(axis=1).values.reshape(-1, 1)
    return clr_data


st.title("PCA Analysis")

st.write("""
Principal Component Analysis (PCA) is a powerful tool for reducing the dimensionality of your data while preserving as much variance as possible. 
On this page, you can perform PCA on your food counts data, visualize the results, and explore how different components contribute to the variance in your dataset.
""")

if 'food_counts_generated' in st.session_state and st.session_state.food_counts_generated:
    st.sidebar.header("PCA Settings")

    level = st.sidebar.selectbox(
        "Select hierarchy level", [0, 1, 2, 3, 4, 5, 6], index=3,
        help="Choose the hierarchy level for the food data, with higher levels offering more detailed categories."
    )
    food_counts = st.session_state.food_counts[st.session_state.food_counts['level'] == level]
    food_counts = food_counts.pivot_table(index='filename', columns='food_type', values='count', fill_value=0)
    group_df = st.session_state.food_counts[['filename', 'group']].drop_duplicates().set_index('filename')
    food_counts = food_counts.join(group_df)
    data = food_counts

    st.subheader('Rename Group Values')
    st.write("""
    You can rename group values to better reflect the categories in your analysis. This helps in tailoring the output to your specific needs or making it more intuitive for others who may view your results.
    """)
    
    group_values = data['group'].unique()
    new_group_names = {}
    
    for value in group_values:
        new_name = st.text_input(f'New name for {value}', value)
        new_group_names[value] = new_name
    
    data['group'] = data['group'].map(new_group_names)

    st.write("### Data Preview")
    st.write("""
    Here is a preview of your data after applying the selected hierarchy level and renaming group values. 
    This data will be used for the PCA analysis.
    """)
    st.write(data.head())

    default_features = [col for col in data.columns if col != 'group']
    features = st.multiselect("Select features for PCA", default_features, default=default_features)
    n_components = st.sidebar.slider(
        "Select number of principal components", 2, min(len(features), 10), 2,
        help="Choose the number of principal components to retain in the analysis."
    )

    apply_clr = st.sidebar.checkbox(
        "Apply CLR Transformation", value=False,
        help="Center Log Ratio (CLR) transformation is useful for compositional data. Check this box to apply CLR before PCA."
    )

    clr_offset = st.sidebar.number_input(
        "CLR Offset", min_value=0.0, value=1.0,
        help="Set the offset value to avoid taking the log of zero during CLR transformation."
    )

    if 'pca_df' not in st.session_state or st.session_state.n_components != n_components or st.session_state.features != features or st.session_state.apply_clr != apply_clr or st.session_state.clr_offset != clr_offset:
        if len(features) < 2:
            st.error("Please select at least two features.")
        else:
            pca_df, explained_variance_df, pca_columns = run_pca(data, features, n_components, apply_clr, clr_offset)
            st.session_state.pca_df = pca_df
            st.session_state.explained_variance_df = explained_variance_df
            st.session_state.pca_columns = pca_columns
            st.session_state.n_components = n_components
            st.session_state.features = features
            st.session_state.apply_clr = apply_clr
            st.session_state.clr_offset = clr_offset

    pca_df = st.session_state.pca_df
    explained_variance_df = st.session_state.explained_variance_df
    pca_columns = st.session_state.pca_columns

    st.write("### Variance Explained by Principal Components")
    st.write("""
    This bar chart shows the proportion of the total variance in your data explained by each principal component.
    """)
    fig, ax = plt.subplots()
    ax.bar(explained_variance_df['PC'], explained_variance_df['Explained Variance'])
    ax.set_xlabel('Principal Component')
    ax.set_ylabel('Explained Variance Ratio')
    ax.set_title('Variance Explained by Each Principal Component')
    st.pyplot(fig)

    st.sidebar.header("PCs to Visualize")
    x_pc = st.sidebar.selectbox("Select PC for x-axis", pca_columns, index=0)
    y_pc = st.sidebar.selectbox("Select PC for y-axis", pca_columns, index=1)

    st.write("### PCA Result")

    # Sidebar for selecting group colors
    if 'group' in data.columns:
        group_values = data['group'].unique()
        group_colors = {}

        st.sidebar.header("Select Group Colors")
        for group in group_values:
            group_colors[group] = st.sidebar.color_picker(f"Pick a color for {group}", "#0000FF")
    else:
        group_colors = None
    
    if 'group' in data.columns:
        if group_colors:
            color_discrete_map = {group: color for group, color in group_colors.items()}
        else:
            color_discrete_map = None

        fig = px.scatter(
            pca_df, 
            x=x_pc, 
            y=y_pc, 
            color='group', 
            title="PCA Scatter Plot", 
            hover_data=[data.index], 
            template='plotly_white',
            color_discrete_map=color_discrete_map
        )
    else:
        fig = px.scatter(pca_df, x=x_pc, y=y_pc, title="PCA Scatter Plot", template='plotly_white')

    fig.update_layout(
        xaxis=dict(showgrid=True, zeroline=True),
        yaxis=dict(showgrid=True, zeroline=True),
    )

    fig.update_xaxes({'zerolinecolor': 'black'})
    fig.update_yaxes({'zerolinecolor': 'black'})

    fig.update_traces(marker=dict(size=10, line=dict(color='black', width=2), opacity=0.8))

    st.plotly_chart(fig)

else:
    st.warning("Please generate food counts first by navigating to the 'Create Food Counts' tab. You'll need to generate counts before performing PCA.")

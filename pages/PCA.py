import streamlit as st
from streamlit_navigation_bar import st_navbar
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

st.set_page_config(initial_sidebar_state="auto")

page = st_navbar(["Home", "Create Food Counts", "Visualization", "PCA", "Sankey Diagram", "How to use"], selected= 'PCA')

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


# pca_analysis.py


def run_pca(data, features, n_components, apply_clr=False, offset=1):
    if apply_clr:
        transformed_data = clr_transformation(data[features], offset=offset)
        st.write(transformed_data)
    else:
        transformed_data = data[features]
        
    scaled_data = StandardScaler().fit_transform(transformed_data)
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(scaled_data)
    
    # Variance explained by each principal component
    explained_variance = pca.explained_variance_ratio_
    explained_variance_df = pd.DataFrame({
        'PC': [f'PC{i+1}' for i in range(n_components)],
        'Explained Variance': explained_variance
    })

        # Create PCA DataFrame
        # Create PCA DataFrame
    pca_columns = [f'PC{i+1}' for i in range(n_components)]
    pca_df = pd.DataFrame(data=pca_result, columns=pca_columns)
    pca_df = pd.concat([pca_df, data.reset_index(drop=True)], axis=1)
    
    return pca_df, explained_variance_df, pca_columns



def clr_transformation(data, offset=1):
    """Apply Centered Log Ratio (CLR) transformation with an offset."""
    # Replace zeros with a small value to avoid log(0)
    data = data + offset
    log_data = np.log(data)
    clr_data = log_data - log_data.mean(axis=1).values.reshape(-1, 1)
    return clr_data


st.title("PCA Analysis")

if 'food_counts_generated' in st.session_state and st.session_state.food_counts_generated:
    

    
    st.sidebar.header("PCA Settings")
    level = st.sidebar.selectbox("Select hierarchy level",[0,1,2,3,4,5,6], index=3)
    food_counts = st.session_state.food_counts[st.session_state.food_counts['level'] == level]
    food_counts = food_counts.pivot_table(index='filename', columns='food_type', values='count', fill_value=0)
    group_df = st.session_state.food_counts[['filename', 'group']].drop_duplicates().set_index('filename')
    food_counts = food_counts.join(group_df)
    data = food_counts

# Allow users to rename group values
    st.subheader('Rename Group Values')
    group_values = data['group'].unique()
    new_group_names = {}
    
    for value in group_values:
        new_name = st.text_input(f'New name for {value}', value)
        new_group_names[value] = new_name
    
    data['group'] =  data['group'].map(new_group_names)      
    

    st.write("Data Preview", data.head())

    # Default feature selection to all columns except 'group'
    default_features = [col for col in data.columns if col != 'group']
    features = st.multiselect("Select features for PCA", default_features, default=default_features)
    n_components = st.sidebar.slider("Select number of principal components", 2, min(len(features), 10), 2)

    apply_clr = st.sidebar.checkbox("Apply CLR Transformation", value=False)
    clr_offset = st.sidebar.number_input("CLR Offset", min_value=0.0, value=1.0)



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

    # Variance explained plot
    st.write("Variance Explained by Principal Components")
    fig, ax = plt.subplots()
    ax.bar(explained_variance_df['PC'], explained_variance_df['Explained Variance'])
    ax.set_xlabel('Principal Component')
    ax.set_ylabel('Explained Variance Ratio')
    ax.set_title('Variance Explained by Each Principal Component')
    st.pyplot(fig)

    # Select PCs to visualize
    st.sidebar.header("PCs to Visualize")
    x_pc = st.sidebar.selectbox("Select PC for x-axis", pca_columns, index=0)
    y_pc = st.sidebar.selectbox("Select PC for y-axis", pca_columns, index=1)

    # PCA scatter plot
    st.write("PCA Result")
    if 'group' in data.columns:
        fig = px.scatter(pca_df, x=x_pc, y=y_pc, color='group', title="PCA Scatter Plot", hover_data=[data.index], template='plotly_white')
    else:
        fig = px.scatter(pca_df, x=x_pc, y=y_pc, title="PCA Scatter Plot", template='plotly_white')

    # Add grid lines to the scatter plot
    fig.update_layout(
        xaxis=dict(showgrid=True, zeroline=True),
        yaxis=dict(showgrid=True, zeroline=True),
    )

    fig.update_xaxes({'zerolinecolor':'black'})
    fig.update_yaxes({'zerolinecolor':'black'})


    fig.update_traces(marker=dict(size=10, line=dict(color='black', width=2), opacity=0.8))

    st.plotly_chart(fig)

else:
    st.warning("Please generate food counts first.")



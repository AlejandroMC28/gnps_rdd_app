# src/visualization.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import scipy.cluster.hierarchy as sch

def plot_food_counts(df, level):
    fig, ax = plt.subplots(figsize=(10, 6))
    df.sum().plot(kind='bar', ax=ax)
    ax.set_title(f'Food Counts at Level {level}')
    ax.set_xlabel('Food Types')
    ax.set_ylabel('Counts')
    st.pyplot(fig)


def bar_plot_food_counts(filtered_food_counts, group_by=False):

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlabel('Food Type')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set_ylabel('Count')
    ax.set_title('Total Counts of Selected Food Types')
    color_sequence = px.colors.qualitative.Set1

    if group_by == False:
        filtered_no_group = filtered_food_counts.loc[:, filtered_food_counts.columns!='group']
        # Converting to long-form DataFrame
        long_form_df = filtered_no_group.sum().reset_index()
        long_form_df.columns = ['Food Type', 'Count']

        # Creating Plotly bar plot
        fig = px.bar(long_form_df, x='Food Type', y='Count', title='Total Counts of Selected Food Types')


    elif group_by == True:
        grouped_df = filtered_food_counts.groupby('group').sum().reset_index()
        long_form_df = pd.melt(grouped_df, id_vars='group', var_name='Food Type', value_name='Count')
        fig = px.bar(long_form_df, x='Food Type', y='Count', color='group', 
                     title='Grouped Counts of Selected Food Types', barmode='group', 
                     color_discrete_sequence=color_sequence)

   
    st.plotly_chart(fig)


def box_plot_food_proportions(filtered_food_counts, group_by=False):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlabel('Food Type')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set_ylabel('Proportion')
    ax.set_title('Proportion Distribution of Selected Food Types')

    if group_by:
        # Convert the dataframe to long-form, keeping 'group' as an identifier
        long_form_df = pd.melt(filtered_food_counts, id_vars='group', var_name='Food Type', value_name='Count')
        
        # Calculate the total count for each food type across all groups
        total_counts = long_form_df.groupby('Food Type')['Count'].sum().reset_index()
        total_counts.columns = ['Food Type', 'Total Count']
        
        # Merge the total counts back with the long form dataframe
        long_form_df = long_form_df.merge(total_counts, on='Food Type')
        
        # Calculate the proportion of each group's count relative to the total count for each food type
        long_form_df['Proportion'] = long_form_df['Count'] / long_form_df['Total Count']

        # Creating grouped box plot for proportions
        fig = px.box(long_form_df, x='Food Type', y='Proportion', color='group', 
                     title='Grouped Proportion Distribution of Selected Food Types', points='all')

    else:
        # Calculate total counts for each food type
        total_counts = filtered_food_counts.sum().reset_index()
        total_counts.columns = ['Food Type', 'Total Count']
        filtered_no_group = filtered_food_counts.loc[:, filtered_food_counts.columns!='group']
        
        # Convert the dataframe to long-form
        long_form_df = pd.melt(filtered_no_group, var_name='Food Type', value_name='Count')
        
        # Merge the total counts back with the long form dataframe
        long_form_df = long_form_df.merge(total_counts, on='Food Type')
        
        # Calculate the proportion of each count relative to the total count for each food type
        long_form_df['Proportion'] = long_form_df['Count'] / long_form_df['Total Count']

        # Creating regular box plot for proportions
        fig = px.box(long_form_df, x='Food Type', y='Proportion', title='Proportion Distribution of Selected Food Types', points='all')

    #st.write(filtered_food_counts.describe())
    st.plotly_chart(fig)


def show_heatmap(filtered_data, apply_clustering=False):

    groups = filtered_data.set_index('filename')['group']

    # Drop the 'group' column and set 'filename' as the index
    data_wo_group = filtered_data.drop(columns=['group']).set_index('filename')

    if apply_clustering:
        # Perform hierarchical/agglomerative clustering on the proportions
        linked_proportions = sch.linkage(data_wo_group, method='ward')

        # Reorder the data according to the clustering results
        dendro_order = sch.leaves_list(linked_proportions)
        data_reordered = data_wo_group.iloc[dendro_order, :]
        groups_reordered = groups.iloc[dendro_order]

        # Map group colors
        unique_groups = groups_reordered.unique()
        group_colors = {group: color for group, color in zip(unique_groups, sns.color_palette(n_colors=len(unique_groups)))}

        # Create a dendrogram with colored clusters based on groups
        plt.figure(figsize=(10, 4))
        dendro = sch.dendrogram(linked_proportions, labels=data_reordered.index, leaf_rotation=90, color_threshold=None)
        
        ax = plt.gca()
        xlbls = ax.get_xmajorticklabels()
        for lbl in xlbls:
            sample_name = lbl.get_text()
            lbl.set_color(group_colors[groups[sample_name]])

        # Create a legend for the groups
        handles = [plt.Line2D([0], [0], color=color, lw=4) for color in group_colors.values()]
        labels = [f'Group {group}' for group in group_colors.keys()]
        
        plt.legend(handles, labels, title='Groups')
        plt.title('Dendrogram')
        plt.xlabel('Samples')
        plt.ylabel('Distance')
        plt.tight_layout()
        st.pyplot(plt.gcf())
    else:
        data_reordered = data_wo_group
    # Create a heatmap
    fig_heatmap = px.imshow(data_reordered.T,
                        labels={'x': 'Filenames', 'y': 'Features', 'color': 'Proportions'},
                        x=data_reordered.index,
                        y=data_reordered.columns,
                        aspect='auto')

    # Adjust the figure size
    fig_heatmap.update_layout(width=1000, height=800)

    # Display the heatmap
    st.plotly_chart(fig_heatmap)


    



def transform_to_proportions(df):
    # Calculate proportions for each row, using only numeric columns
    numeric_cols = df.select_dtypes(include=[float, int]).columns
    df_proportions = df[numeric_cols].apply(lambda x: x / x.sum() if x.sum() != 0 else x, axis=1)
    # Combine back with non-numeric columns
    non_numeric_cols = df.select_dtypes(exclude=[float, int])
    df_proportions = pd.concat([df_proportions, non_numeric_cols], axis=1)
    return df_proportions

# def box_plot_food_proportions_2(filtered_food_counts, group_by=False):
#     # Transform to proportions
    
#     filtered_food_counts = transform_to_proportions(filtered_food_counts)
#     st.write(filtered_food_counts)

#     if group_by:
#         # Melt the DataFrame to long form with group column
#         long_form_df = pd.melt(filtered_food_counts, id_vars='group', var_name='Food Type', value_name='Proportion')
#         st.write(long_form_df)
#         long_form_df.rename(columns={'index': 'Filename'}, inplace=True)

#         # Creating grouped box plot for proportions
#         fig = px.box(long_form_df, x='Food Type', y='Proportion', color='group', 
#                      title='Grouped Proportion Distribution of Selected Food Types',
#                      points="all")
#     else:
#         # Melt the DataFrame to long form without group column
#         long_form_df = pd.melt(filtered_food_counts.reset_index(), id_vars=['index'], var_name='Food Type', value_name='Proportion')
#         long_form_df.rename(columns={'index': 'Filename'}, inplace=True)

#         # Creating regular box plot for proportions
#         fig = px.box(long_form_df, x='Food Type', y='Proportion', 
#                      title='Proportion Distribution of Selected Food Types',
#                      points="all")

#     st.plotly_chart(fig)
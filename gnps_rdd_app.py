import os
import streamlit as st
from streamlit_navigation_bar import st_navbar
import pages as pg
import importlib
import pages.home as home
import pages.PCA
import pages.sankey_diagram
import pages.dynamic_filtering_visualization
import pages.create_food_counts

""" importlib.reload(pages.home)
importlib.reload(pages.PCA)
importlib.reload(pages.sankey_diagram)
importlib.reload(pages.dynamic_filtering_visualization)
importlib.reload(pages.create_food_counts)
# Force reload of modules during development
importlib.reload(pg) """


st.set_page_config(
    page_title="GNPS-RDD app", page_icon="🍋", initial_sidebar_state="auto"
)

pages = [
    "Home",
    "Create count table",
    "Dynamic filtering & visualization",
    "PCA",
    "Sankey Diagram",
]

parent_dir = os.path.dirname(os.path.abspath(__file__))

styles = {
    "nav": {
        "background-color": "royalblue",
        "justify-content": "left",
    },
    "img": {
        "padding-right": "14px",
    },
    "span": {
        "color": "white",
        "padding": "14px",
    },
    "active": {
        "background-color": "white",
        "color": "var(--text-color)",
        "font-weight": "normal",
        "padding": "14px",
    },
}
options = {
    "show_menu": True,
    "show_sidebar": True,
}

page = st_navbar(
    pages,
    styles=styles,
    options=options,
)

functions = {
    "Home": pg.show_home,
    "Create Food Counts": pg.show_create_food_counts,
    "Dynamic filtering & visualization": pg.show_visualization,
}
go_to = functions.get(page)
if go_to:
    go_to()

st.write(page)

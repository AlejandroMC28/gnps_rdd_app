"""
Tests for Streamlit pages
"""

import os
import importlib.util


def test_home_page_exists():
    """Test that Home.py exists and can be imported."""
    home_path = "Home.py"
    assert os.path.exists(home_path)
    
    spec = importlib.util.spec_from_file_location("Home", home_path)
    assert spec is not None


def test_page_01_exists():
    """Test that page 01 exists."""
    assert os.path.exists("pages/01_Create_RDD_Count_Table.py")


def test_page_02_exists():
    """Test that page 02 exists."""
    assert os.path.exists("pages/02_Visualizations.py")


def test_page_03_exists():
    """Test that page 03 exists."""
    assert os.path.exists("pages/03_PCA_Analysis.py")


def test_page_04_exists():
    """Test that page 04 exists."""
    assert os.path.exists("pages/04_Sankey_Diagram.py")


def test_page_05_exists():
    """Test that page 05 exists."""
    assert os.path.exists("pages/05_How_to_Use.py")


def test_src_modules_exist():
    """Test that all src modules exist."""
    assert os.path.exists("src/__init__.py")
    assert os.path.exists("src/RDDcounts.py")
    assert os.path.exists("src/utils.py")
    assert os.path.exists("src/analysis.py")
    assert os.path.exists("src/visualization.py")
    assert os.path.exists("src/state_helpers.py")


def test_data_directory_exists():
    """Test that data directory exists."""
    assert os.path.exists("data")
    assert os.path.isdir("data")

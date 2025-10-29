"""
Tests for analysis functions in src/analysis.py
"""

import inspect
from src.analysis import perform_pca_RDD_counts


def test_perform_pca_function_exists():
    """Test that perform_pca_RDD_counts function exists and is callable."""
    assert callable(perform_pca_RDD_counts)


def test_perform_pca_has_correct_signature():
    """Test that perform_pca has the expected parameters."""
    sig = inspect.signature(perform_pca_RDD_counts)
    assert "RDD_counts_instance" in sig.parameters
    assert "level" in sig.parameters
    assert "n_components" in sig.parameters
    assert "apply_clr" in sig.parameters

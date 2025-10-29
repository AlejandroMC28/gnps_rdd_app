"""
Tests for the RDDCounts class in src/RDDcounts.py
"""

import pandas as pd
import pytest
from src.RDDcounts import RDDCounts


def test_rddcounts_invalid_initialization():
    """Test that RDDCounts raises error when both task_id and gnps_network_path are provided."""
    with pytest.raises(ValueError, match="Provide exactly one"):
        RDDCounts(
            gnps_network_path="path.tsv",
            task_id="123456",
            sample_types="simple",
        )


def test_rddcounts_no_input_error():
    """Test that RDDCounts raises error when neither task_id nor gnps_network_path provided."""
    with pytest.raises(ValueError, match="Provide exactly one"):
        RDDCounts(sample_types="simple")


def test_rddcounts_has_required_methods():
    """Test that RDDCounts has expected methods."""
    assert hasattr(RDDCounts, "__init__")
    assert hasattr(RDDCounts, "create_RDD_counts_all_levels")
    assert hasattr(RDDCounts, "filter_counts")
    assert hasattr(RDDCounts, "file_counts")
    assert hasattr(RDDCounts, "update_groups")
    assert hasattr(RDDCounts, "generate_RDDflows")

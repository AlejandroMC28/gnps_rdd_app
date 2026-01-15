"""
Tests for utility functions in rdd.utils module
"""

import pandas as pd
import pytest
from rdd.utils import (
    _load_RDD_metadata,
    remove_filename_extension,
    RDD_counts_to_wide,
)


def test_load_rdd_metadata_internal():
    """Test loading internal reference metadata."""
    metadata = _load_RDD_metadata()
    assert isinstance(metadata, pd.DataFrame)
    assert "filename" in metadata.columns
    assert len(metadata) > 0


def test_load_rdd_metadata_invalid_format(tmp_path):
    """Test that invalid file format raises ValueError."""
    invalid_file = tmp_path / "invalid.xyz"
    invalid_file.write_text("data")

    with pytest.raises(ValueError, match="must be a CSV, TSV, or TXT"):
        _load_RDD_metadata(str(invalid_file))


def test_load_rdd_metadata_file_not_found():
    """Test that non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        _load_RDD_metadata("/nonexistent/file.csv")


def test_remove_filename_extension():
    """Test filename extension removal."""
    series1 = pd.Series(["file.mzML"])
    series2 = pd.Series(["file.mzXML"])
    series3 = pd.Series(["file.txt"])

    assert remove_filename_extension(series1)[0] == "file"
    assert remove_filename_extension(series2)[0] == "file"
    assert remove_filename_extension(series3)[0] == "file"


def test_remove_filename_extension_series():
    """Test filename extension removal on pandas Series."""
    series = pd.Series(["file1.mzML", "file2.mzXML", "file3.txt"])
    result = remove_filename_extension(series)
    assert isinstance(result, pd.Series)
    assert result[0] == "file1"
    assert result[1] == "file2"
    assert result[2] == "file3"


def test_rdd_counts_to_wide():
    """Test conversion of RDD counts to wide format."""
    counts_df = pd.DataFrame(
        {
            "filename": ["sample1", "sample1", "sample2", "sample2"],
            "reference_type": ["Type_A", "Type_B", "Type_A", "Type_B"],
            "count": [10, 20, 15, 25],
            "level": [1, 1, 1, 1],
            "group": ["G1", "G1", "G2", "G2"],
        }
    )

    wide_df = RDD_counts_to_wide(counts_df, level=1)
    assert isinstance(wide_df, pd.DataFrame)
    assert "Type_A" in wide_df.columns
    assert "Type_B" in wide_df.columns
    assert "group" in wide_df.columns
    assert len(wide_df) == 2

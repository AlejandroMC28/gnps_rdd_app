"""
Test fixtures and configuration for the test suite.
"""

import pytest


@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {"test": "data"}

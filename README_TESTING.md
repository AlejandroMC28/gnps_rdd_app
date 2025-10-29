# Testing

## Running Tests

```bash
# Run all tests
make test

# Or using pytest directly
pytest

# Run with verbose output
pytest -v
```

## Test Structure

- `tests/test_analysis.py` - Tests for PCA analysis functions
- `tests/test_rddcounts.py` - Tests for RDDCounts class
- `tests/test_utils.py` - Tests for utility functions
- `tests/test_streamlit_pages.py` - Tests for Streamlit app structure

## Code Quality

```bash
# Check code with linting
make lint

# Auto-format code
make format
```

## CI/CD

Tests run automatically on push/PR to main branch via GitHub Actions.

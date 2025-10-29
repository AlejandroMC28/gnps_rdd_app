.PHONY: help install install-dev test lint format clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting (flake8)"
	@echo "  make format       - Format code with black and isort"
	@echo "  make clean        - Remove cache and test files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest

lint:
	flake8 src pages tests --count --select=E9,F63,F7,F82 --show-source --statistics

format:
	black src pages tests
	isort src pages tests

clean:
	rm -rf __pycache__ .pytest_cache htmlcov .coverage coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

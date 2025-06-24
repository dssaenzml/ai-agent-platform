.PHONY: help test test-unit test-integration test-api test-coverage lint format clean install-dev

help:
	@echo "Available commands:"
	@echo "  install-dev      Install development dependencies"
	@echo "  test            Run all tests"
	@echo "  test-unit       Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-api        Run API tests only"
	@echo "  test-coverage   Run tests with coverage report"
	@echo "  lint            Run code linting"
	@echo "  format          Format code with black and isort"
	@echo "  clean           Clean up cache and temporary files"

install-dev:
	poetry install --with dev

test:
	poetry run pytest

test-unit:
	poetry run pytest tests/unit -m unit

test-integration:
	poetry run pytest tests/integration -m integration

test-api:
	poetry run pytest -m api

test-coverage:
	poetry run pytest --cov=app --cov-report=html --cov-report=term

lint:
	poetry run flake8 app tests
	poetry run mypy app

format:
	poetry run black app tests
	poetry run isort app tests

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

run-dev:
	poetry run uvicorn app.server:app --reload --host 0.0.0.0 --port 8080

run-tests-watch:
	poetry run pytest-watch 
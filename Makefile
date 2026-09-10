.PHONY: install test run clean

install:
	python -m pip install --upgrade pip
	python -m pip install -e .[dev]

test:
	pytest

run:
	python run_pipeline.py

clean:
	rm -rf data outputs .pytest_cache

# Load variables from .env (if present) and pass them to every command
-include .env
export

DBT_FLAGS = --project-dir dbt --profiles-dir dbt

.PHONY: install test sample build docs report all prod clean

install:
	pip install -r requirements.txt

test:
	python -m pytest -q

sample:
	python -m ingestion.run_pipeline --source sample --target duckdb

build:
	dbt build $(DBT_FLAGS)

docs:
	dbt docs generate $(DBT_FLAGS) && dbt docs serve $(DBT_FLAGS)

report:
	python analysis/report.py

all: test sample build report

prod:
	python -m ingestion.run_pipeline --source live --target bigquery
	dbt build $(DBT_FLAGS) --target prod

clean:
	rm -rf data dbt/target dbt/logs logs

install:
	uv sync

ingest:
	uv run python -m nyc_tlc.ingest.run

clean:
	uv run python -m nyc_tlc.clean.run

dbt-run:
	cd dbt_project && uv run dbt run --profiles-dir .

train:
	uv run python -m nyc_tlc.ml.train

flow:
	uv run python prefect_flows/main_flow.py

dashboard:
	uv run streamlit run src/nyc_tlc/dashboard/Home.py

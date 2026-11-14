# Retail Sales Data Engineering Platform

End-to-end retail data platform: Python ingestion → Amazon S3 → Snowflake (Bronze/Silver/Gold) → dbt → Airflow (Docker) → Power BI.

> **Status: Phase 1 – requirements and setup.** Later phases are added one at a time: build, test, document, commit.

## Data sources
| Source | Role | Notes |
|---|---|---|
| [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) | Primary historical transactions | Real UK online-retail invoices, Dec 2009 – Dec 2011. Manual download. |
| [DummyJSON](https://dummyjson.com/docs) products / carts / users | API ingestion practice | **Synthetic demo data.** Not Tesco or any real retailer. |

This project is not a live integration with Tesco or any retailer. See `docs/source_notes.md`.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env

# 1. Download the UCI zip from the page above, extract online_retail_II.xlsx into data/raw/
# 2. Fetch the API extracts
python -m ingestion.fetch_dummyjson
# 3. Profile everything (writes docs/source_profile.md)
python -m ingestion.profile_data
# 4. Tests
pytest
```

## Structure
`dags/` Airflow · `ingestion/` extract scripts · `src/` shared code · `dbt/retail_analytics/` models · `sql/` Snowflake setup · `docker/` Airflow compose · `docs/` architecture, dictionary, decisions · `tests/` Python tests

## Security
Never commit `.env`, keys, passwords or raw datasets (all gitignored). Use IAM roles / Snowflake storage integrations rather than embedded credentials.

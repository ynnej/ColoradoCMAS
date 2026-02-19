# Colorado CMAS District Dashboard

This project fetches Colorado CMAS ELA Grade 3 district-level data and serves a Streamlit dashboard.

## Files

- `fetch_cmas_co.py`: scraper/ETL script.
- `app.py`: Streamlit dashboard.
- `data/raw/`: cached HTML responses.
- `data/cmas_ela_grade3_district.csv`: output dataset.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Fetch Data

```bash
python fetch_cmas_co.py
```

Optional debug mode (first N districts):

```bash
python fetch_cmas_co.py --limit 10
```

## Run Dashboard

```bash
streamlit run app.py
```

## Notes

- The fetcher uses retries, timeout handling, and raw-response caching to `data/raw/`.
- The district-code source is currently an official `.xlsx` file at the CDE URL and is parsed automatically.
- Suppressed/missing values like `--` are written as blank values in the CSV.
- If district pages change structure, the parser uses multiple extraction strategies and keeps missing fields as nulls instead of failing the full run.
- The scraper includes a BeautifulSoup table-parser fallback, so it works even if optional `pandas.read_html` engines (like `lxml`) are not installed.

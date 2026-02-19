# Colorado CMAS District Dashboard

This project builds a Colorado CMAS ELA Grade 3 district dataset and serves a Streamlit dashboard.

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

## Build Data

### Offline (recommended if CDE site is blocked)

Place the official summary export at:

- `data/CMAS_Summary_CMAS_ELA_and_Math.csv`

Then run:

```bash
python fetch_cmas_co.py
```

This extracts district-level Grade 3 ELA values and writes:

- `data/cmas_ela_grade3_district.csv`

### Web Scrape Mode

If you have direct access to CDE pages, you can still use scraping:

```bash
python fetch_cmas_co.py --force-web
```

Optional debug mode (first N districts):

```bash
python fetch_cmas_co.py --limit 10 --force-web
```

## Run Dashboard

```bash
streamlit run app.py
```

## Notes

- `app.py` auto-builds `data/cmas_ela_grade3_district.csv` from `data/CMAS_Summary_CMAS_ELA_and_Math.csv` if needed.
- The fetcher uses retries, timeout handling, and raw-response caching to `data/raw/` when web mode is used.
- The district-code source is currently an official `.xlsx` file at the CDE URL and is parsed automatically.
- Suppressed/missing values like `--` are written as blank values in the CSV.
- If district pages change structure, the parser uses multiple extraction strategies and keeps missing fields as nulls instead of failing the full run.
- The scraper includes a BeautifulSoup table-parser fallback, so it works even if optional `pandas.read_html` engines (like `lxml`) are not installed.

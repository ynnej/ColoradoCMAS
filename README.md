# Colorado CMAS District Dashboard

This project builds a Colorado CMAS ELA Grade 3 district dataset and serves a Streamlit dashboard.

## Live App

- [Colorado CMAS Dashboard](https://coloradocmas-rfvwhu5u7yah5j7wk2mjku.streamlit.app/)

## Files

- `fetch_cmas_co.py`: scraper/ETL script.
- `app.py`: Streamlit dashboard.
- `data/raw/`: cached HTML responses.
- `data/cmas_ela_grade3_district.csv`: output dataset.
- `runtime.txt`: pins Streamlit Community Cloud to Python 3.12.

## Local Setup (Python 3.12)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `python3.12` is not installed, install it first (for example with `pyenv`) and then rerun the commands above.

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

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. In Streamlit Community Cloud, choose `Create app`.
3. Use the interactive picker (or enter equivalent values):
   - Repository: `ynnej/ColoradoCMAS`
   - Branch: `main`
   - Main file path: `app.py`
4. Click `Deploy`.

Important: do not paste the GitHub `blob/.../app.py` page URL as the repo URL field. Use repo + branch + file path.

## Notes

- `app.py` auto-builds `data/cmas_ela_grade3_district.csv` from `data/CMAS_Summary_CMAS_ELA_and_Math.csv` if needed.
- The fetcher uses retries, timeout handling, and raw-response caching to `data/raw/` when web mode is used.
- The district-code source is currently an official `.xlsx` file at the CDE URL and is parsed automatically.
- Suppressed/missing values like `--` are written as blank values in the CSV.
- If district pages change structure, the parser uses multiple extraction strategies and keeps missing fields as nulls instead of failing the full run.
- `requirements.txt` includes `lxml` to support `pandas.read_html` in environments where it is available.

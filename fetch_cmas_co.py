#!/usr/bin/env python3
"""Fetch Colorado CMAS ELA Grade 3 district metrics into CSV.

This script:
1) Loads district codes from Colorado CDE's official administrative unit page.
2) Fetches CMAS ELA district pages for each district code.
3) Extracts latest school year + Grade 3 district metrics.
4) Writes data/cmas_ela_grade3_district.csv.
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import re
import sys
import zipfile
from dataclasses import dataclass
from io import BytesIO, StringIO
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DISTRICT_CODES_URL = "https://www.cde.state.co.us/datapipeline/administrativeunitanddistrictcodes"
CMAS_ELA_URL_TEMPLATE = "https://www.cde.state.co.us/schoolview/explore/cmasela/{district_code}"
OUTPUT_CSV = Path("data/cmas_ela_grade3_district.csv")
RAW_DIR = Path("data/raw")
SUMMARY_SOURCE_CSV = Path("data/CMAS_Summary_CMAS_ELA_and_Math.csv")


@dataclass
class DistrictRecord:
    district_name: str | None
    district_code: str
    school_year: str | None
    grade_3_percent_met_or_exceeded_district: float | None
    grade_3_participation_rate_district: float | None


def build_session() -> requests.Session:
    retry = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": "ColoradoCMASDashboard/1.0 (+https://www.cde.state.co.us)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )
    return session


def fetch_html(session: requests.Session, url: str, cache_path: Path, timeout: int = 30) -> str:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8", errors="ignore")

    logging.info("Fetching %s", url)
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    html = response.text
    cache_path.write_text(html, encoding="utf-8")
    return html


def fetch_bytes(session: requests.Session, url: str, cache_path: Path, timeout: int = 30) -> bytes:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        return cache_path.read_bytes()

    logging.info("Fetching %s", url)
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.content
    cache_path.write_bytes(data)
    return data


def is_xlsx_bytes(data: bytes) -> bool:
    if not data.startswith(b"PK\x03\x04"):
        return False

    try:
        with zipfile.ZipFile(BytesIO(data)) as workbook:
            names = set(workbook.namelist())
    except zipfile.BadZipFile:
        return False

    return "[Content_Types].xml" in names and "xl/workbook.xml" in names


def normalize_code(value: object) -> str | None:
    text = str(value).strip()
    if not text:
        return None
    m = re.fullmatch(r"(\d{1,4})", text)
    if not m:
        return None
    return m.group(1).zfill(4)


def extract_codes_from_tables(html: str) -> set[str]:
    codes: set[str] = set()
    soup = BeautifulSoup(html, "html.parser")

    for row in soup.select("table tr"):
        cells = [c.get_text(" ", strip=True) for c in row.select("th,td")]
        if not cells:
            continue
        row_has_name = any(re.search(r"[A-Za-z]", c) for c in cells)
        if not row_has_name:
            continue
        for cell in cells:
            code = normalize_code(cell)
            if code:
                codes.add(code)

    for df in read_html_tables(html):
        for col in df.columns:
            col_str = str(col).strip().lower()
            if "district" in col_str or "code" in col_str or "number" in col_str:
                series = df[col].dropna().astype(str)
                for value in series:
                    code = normalize_code(value)
                    if code:
                        codes.add(code)
        for value in df.astype(str).values.ravel().tolist():
            code = normalize_code(value)
            if code:
                codes.add(code)

    for match in re.findall(r"/schoolview/explore/cmasela/(\d{4})", html):
        codes.add(match)

    return codes


def extract_codes_from_excel_bytes(data: bytes) -> set[str]:
    try:
        sheets = pd.read_excel(BytesIO(data), sheet_name=None, header=None, dtype=str)
    except ImportError as exc:
        raise RuntimeError(
            "District code source is Excel; install openpyxl (pip install openpyxl) to parse it."
        ) from exc

    codes: set[str] = set()
    for _, df in sheets.items():
        if df.empty:
            continue

        header_row_idx: int | None = None
        district_col_idxs: list[int] = []

        for row_idx in range(len(df)):
            row_values = [str(v).strip() if pd.notna(v) else "" for v in df.iloc[row_idx].tolist()]
            row_lower = [v.lower() for v in row_values]
            if "district code" in row_lower:
                header_row_idx = row_idx
                district_col_idxs = [i for i, cell in enumerate(row_lower) if cell == "district code"]
                break

        if header_row_idx is None or not district_col_idxs:
            continue

        for row_idx in range(header_row_idx + 1, len(df)):
            for col_idx in district_col_idxs:
                code = normalize_code(df.iat[row_idx, col_idx])
                if code:
                    codes.add(code)

    return codes


def load_district_code_source(session: requests.Session) -> tuple[str, str | bytes]:
    xlsx_cache = RAW_DIR / "district_codes_page.xlsx"
    legacy_html_cache = RAW_DIR / "district_codes_page.html"

    if xlsx_cache.exists():
        data = xlsx_cache.read_bytes()
        if is_xlsx_bytes(data):
            return "xlsx", data

    if legacy_html_cache.exists():
        legacy_data = legacy_html_cache.read_bytes()
        if is_xlsx_bytes(legacy_data):
            xlsx_cache.parent.mkdir(parents=True, exist_ok=True)
            xlsx_cache.write_bytes(legacy_data)
            return "xlsx", legacy_data

    response = session.get(DISTRICT_CODES_URL, timeout=30)
    response.raise_for_status()
    content_type = (response.headers.get("content-type") or "").lower()
    data = response.content

    if "spreadsheetml" in content_type or "excel" in content_type or is_xlsx_bytes(data):
        xlsx_cache.parent.mkdir(parents=True, exist_ok=True)
        xlsx_cache.write_bytes(data)
        return "xlsx", data

    html = response.text
    legacy_html_cache.parent.mkdir(parents=True, exist_ok=True)
    legacy_html_cache.write_text(html, encoding="utf-8")
    return "html", html


def extract_district_codes(session: requests.Session) -> list[str]:
    source_type, payload = load_district_code_source(session)
    if source_type == "xlsx":
        blob = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        codes = sorted(extract_codes_from_excel_bytes(blob))
    else:
        html = payload if isinstance(payload, str) else payload.decode("utf-8", errors="ignore")
        codes = sorted(extract_codes_from_tables(html))
    if not codes:
        raise RuntimeError("No district codes found on official district code page.")
    logging.info("Found %d district codes", len(codes))
    return codes


def to_float_or_none(value: object) -> float | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = s.replace("%", "").replace(",", "").strip()
    if "<" in s:
        return None
    if s.lower() in {"--", "- -", "*", "n<16", "n/a", "na", "nan", "none"}:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def extract_school_years(html: str) -> list[str]:
    years = set(re.findall(r"\b(20\d{2}\s*[-/]\s*20\d{2})\b", html))
    normalized = {re.sub(r"\s*[-/]\s*", "-", y) for y in years}
    return sorted(normalized)


def pick_latest_school_year(years: Iterable[str]) -> str | None:
    def key(y: str) -> tuple[int, int]:
        a, b = y.split("-")
        return int(a), int(b)

    years_list = list(years)
    if not years_list:
        return None

    current_year = dt.date.today().year
    plausible = []
    for year in years_list:
        try:
            start, end = key(year)
        except ValueError:
            continue
        if start >= 2000 and end == start + 1 and start <= current_year + 1:
            plausible.append(year)

    candidates = plausible if plausible else years_list
    return max(candidates, key=key)


def extract_district_name(soup: BeautifulSoup, district_code: str) -> str | None:
    def clean_name(text: str) -> str:
        name = re.sub(r"\s+", " ", text).strip()
        name = re.sub(rf"\(\s*{re.escape(district_code)}\s*\)", "", name).strip()
        return name.strip(" -|")

    code_marker = f"({district_code})"
    for heading in soup.select("h1,h2,h3"):
        text = heading.get_text(" ", strip=True)
        if code_marker in text:
            cleaned = clean_name(text)
            if cleaned:
                return cleaned

    district_link = soup.select_one(f"a.address-name[href$='/{district_code}']")
    if district_link:
        cleaned = clean_name(district_link.get_text(" ", strip=True))
        if cleaned:
            return cleaned

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if title:
        text = re.sub(r"\s+", " ", title)
        text = re.sub(r"^SchoolView:\s*", "", text, flags=re.IGNORECASE).strip(" -|")
        if text and text.lower() not in {"school and district data", "cmas english language arts"}:
            return text
    return None


def extract_metrics_from_tables(html: str, latest_year: str | None) -> tuple[float | None, float | None]:
    tables = read_html_tables(html)
    if not tables:
        return None, None

    met_val: float | None = None
    part_val: float | None = None

    for table in tables:
        df = table.copy()
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("")

        year_mask = None
        if latest_year:
            flat_year_match = df.astype(str).apply(lambda col: col.str.contains(latest_year, regex=False)).any(axis=1)
            year_mask = flat_year_match

        for _, row in df.iterrows():
            row_text = " | ".join(str(v) for v in row.values)
            row_text_l = row_text.lower()
            if "grade 3" not in row_text_l:
                continue
            if year_mask is not None and latest_year not in row_text:
                # Keep scanning: some tables separate year in nearby header instead of row.
                pass

            values = [to_float_or_none(v) for v in row.values]
            values = [v for v in values if v is not None and -1 <= v <= 100]
            if not values:
                continue

            if met_val is None and ("met" in row_text_l or "exceed" in row_text_l):
                met_val = values[0]
            if part_val is None and "participation" in row_text_l:
                part_val = values[0]

            # If row doesn't label metrics, try infer if it contains both signals.
            if met_val is None and part_val is None and len(values) >= 2:
                # Heuristic: CMAS metric often listed before participation in summary rows.
                met_val = values[0]
                part_val = values[1]

        # Column-based fallback for tables with explicit metric columns.
        metric_col = next((c for c in df.columns if "met" in c.lower() and "exceed" in c.lower()), None)
        part_col = next((c for c in df.columns if "participation" in c.lower()), None)
        grade_col = next((c for c in df.columns if "grade" in c.lower()), None)
        if grade_col and (metric_col or part_col):
            mask = df[grade_col].astype(str).str.contains(r"grade\s*3", case=False, regex=True)
            subset = df[mask]
            if not subset.empty:
                if metric_col and met_val is None:
                    met_val = to_float_or_none(subset.iloc[0][metric_col])
                if part_col and part_val is None:
                    part_val = to_float_or_none(subset.iloc[0][part_col])

    return met_val, part_val


def table_tag_to_df(table: BeautifulSoup) -> pd.DataFrame | None:
    rows: list[list[str]] = []
    for tr in table.select("tr"):
        cells = tr.select("th,td")
        if not cells:
            continue
        rows.append([c.get_text(" ", strip=True) for c in cells])

    if not rows:
        return None

    width = max(len(r) for r in rows)
    normalized = [r + [""] * (width - len(r)) for r in rows]
    header = normalized[0]

    if any(h.strip() for h in header) and len(normalized) > 1:
        columns = [h.strip() or f"col_{i + 1}" for i, h in enumerate(header)]
        return pd.DataFrame(normalized[1:], columns=columns)

    return pd.DataFrame(normalized)


def read_html_tables(html: str) -> list[pd.DataFrame]:
    try:
        return pd.read_html(StringIO(html))
    except (ValueError, ImportError):
        # Fallback when optional parsers like lxml/html5lib are unavailable.
        pass

    soup = BeautifulSoup(html, "html.parser")
    tables: list[pd.DataFrame] = []
    for table in soup.select("table"):
        df = table_tag_to_df(table)
        if df is not None:
            tables.append(df)
    return tables


def extract_metrics_by_regex(html: str, latest_year: str | None) -> tuple[float | None, float | None]:
    haystack = re.sub(r"\s+", " ", html)
    year_snippet = latest_year if latest_year else ""

    met_patterns = [
        rf"{re.escape(year_snippet)}.{0,1200}?grade\s*3.{0,800}?met.{0,200}?exceed.{0,200}?(\d{{1,3}}(?:\.\d+)?)%",
        r"grade\s*3.{0,800}?met.{0,200}?exceed.{0,200}?(\d{1,3}(?:\.\d+)?)%",
    ]
    part_patterns = [
        rf"{re.escape(year_snippet)}.{0,1200}?grade\s*3.{0,800}?participation.{0,200}?(\d{{1,3}}(?:\.\d+)?)%",
        r"grade\s*3.{0,800}?participation.{0,200}?(\d{1,3}(?:\.\d+)?)%",
    ]

    met_val = None
    part_val = None

    for pattern in met_patterns:
        m = re.search(pattern, haystack, flags=re.IGNORECASE)
        if m:
            met_val = to_float_or_none(m.group(1))
            if met_val is not None:
                break

    for pattern in part_patterns:
        m = re.search(pattern, haystack, flags=re.IGNORECASE)
        if m:
            part_val = to_float_or_none(m.group(1))
            if part_val is not None:
                break

    return met_val, part_val


def parse_cmas_page(html: str, district_code: str) -> DistrictRecord:
    soup = BeautifulSoup(html, "html.parser")
    school_year = pick_latest_school_year(extract_school_years(html))
    district_name = extract_district_name(soup, district_code)

    met, part = extract_metrics_from_tables(html, school_year)
    if met is None or part is None:
        met2, part2 = extract_metrics_by_regex(html, school_year)
        met = met if met is not None else met2
        part = part if part is not None else part2

    return DistrictRecord(
        district_name=district_name,
        district_code=district_code,
        school_year=school_year,
        grade_3_percent_met_or_exceeded_district=met,
        grade_3_participation_rate_district=part,
    )


def fetch_district_record(session: requests.Session, district_code: str) -> DistrictRecord:
    url = CMAS_ELA_URL_TEMPLATE.format(district_code=district_code)
    cache_path = RAW_DIR / f"cmasela_{district_code}.html"
    html = fetch_html(session, url, cache_path)
    return parse_cmas_page(html, district_code)


def records_to_df(records: list[DistrictRecord]) -> pd.DataFrame:
    df = pd.DataFrame([r.__dict__ for r in records])
    df = df.sort_values(by=["district_code"], kind="stable").reset_index(drop=True)
    return df


def infer_assessment_year(columns: Iterable[str]) -> int | None:
    current_year = dt.date.today().year
    years: list[int] = []
    for col in columns:
        text = str(col).strip()
        m = re.fullmatch(r"(20\d{2})", text)
        if m:
            year = int(m.group(1))
            if 2000 <= year <= current_year + 1:
                years.append(year)
            continue
        m = re.fullmatch(r"Participation Rate (20\d{2})", text)
        if m:
            year = int(m.group(1))
            if 2000 <= year <= current_year + 1:
                years.append(year)

    return max(years) if years else None


def school_year_from_assessment_year(assessment_year: int | None) -> str | None:
    if assessment_year is None:
        return None
    return f"{assessment_year - 1}-{assessment_year}"


def extract_records_from_summary_csv(summary_csv: Path, limit: int | None = None) -> list[DistrictRecord]:
    if not summary_csv.exists():
        raise FileNotFoundError(f"Summary CSV not found: {summary_csv}")

    # The CDE summary export includes a preamble; row 18 (0-index 17) contains the table columns.
    summary_df = pd.read_csv(summary_csv, header=17, dtype=str)
    summary_df = summary_df.dropna(how="all")

    required_cols = {"Level", "District Code", "District Name", "Content", "Grade"}
    missing = required_cols.difference(summary_df.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise RuntimeError(f"Summary CSV missing expected columns: {missing_list}")

    assessment_year = infer_assessment_year(summary_df.columns)
    school_year = school_year_from_assessment_year(assessment_year)
    met_col = str(assessment_year) if assessment_year is not None else None
    participation_col = (
        f"Participation Rate {assessment_year}"
        if assessment_year is not None and f"Participation Rate {assessment_year}" in summary_df.columns
        else None
    )

    level = summary_df["Level"].fillna("").astype(str).str.strip().str.upper()
    content = summary_df["Content"].fillna("").astype(str).str.strip().str.lower()
    grade = summary_df["Grade"].fillna("").astype(str).str.strip().str.zfill(2)

    district_rows = summary_df[
        (level == "DISTRICT")
        & (content == "english language arts")
        & (grade == "03")
    ].copy()

    if "School Code" in district_rows.columns:
        school_code = district_rows["School Code"].fillna("").astype(str).str.strip()
        district_rows = district_rows[school_code.isin({"", "0", "0000"})]

    records: list[DistrictRecord] = []
    seen_codes: set[str] = set()

    for _, row in district_rows.iterrows():
        code = normalize_code(row.get("District Code"))
        if not code or code in seen_codes:
            continue
        seen_codes.add(code)

        district_name_raw = str(row.get("District Name", "")).strip()
        district_name = district_name_raw if district_name_raw else None

        met_value = to_float_or_none(row.get(met_col)) if met_col else None
        part_value = to_float_or_none(row.get(participation_col)) if participation_col else None

        records.append(
            DistrictRecord(
                district_name=district_name,
                district_code=code,
                school_year=school_year,
                grade_3_percent_met_or_exceeded_district=met_value,
                grade_3_participation_rate_district=part_value,
            )
        )

    if limit is not None:
        records = records[:limit]

    logging.info(
        "Extracted %d district records from local summary CSV (%s)",
        len(records),
        summary_csv,
    )
    return records


def run(limit: int | None = None, summary_csv: Path | None = None, force_web: bool = False) -> Path:
    if not force_web:
        candidate_summary = summary_csv if summary_csv is not None else SUMMARY_SOURCE_CSV
        if candidate_summary.exists():
            records = extract_records_from_summary_csv(candidate_summary, limit=limit)
            df = records_to_df(records)
            OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(OUTPUT_CSV, index=False)
            logging.info("Wrote %s (%d rows)", OUTPUT_CSV, len(df))
            return OUTPUT_CSV

    session = build_session()
    district_codes = extract_district_codes(session)
    if limit is not None:
        district_codes = district_codes[:limit]

    records: list[DistrictRecord] = []
    for idx, code in enumerate(district_codes, start=1):
        try:
            record = fetch_district_record(session, code)
            records.append(record)
            logging.info(
                "[%d/%d] %s year=%s met=%s part=%s",
                idx,
                len(district_codes),
                code,
                record.school_year,
                record.grade_3_percent_met_or_exceeded_district,
                record.grade_3_participation_rate_district,
            )
        except Exception as exc:  # pylint: disable=broad-except
            logging.warning("[%d/%d] failed district %s: %s", idx, len(district_codes), code, exc)
            records.append(
                DistrictRecord(
                    district_name=None,
                    district_code=code,
                    school_year=None,
                    grade_3_percent_met_or_exceeded_district=None,
                    grade_3_participation_rate_district=None,
                )
            )

    df = records_to_df(records)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    logging.info("Wrote %s (%d rows)", OUTPUT_CSV, len(df))
    return OUTPUT_CSV


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Colorado CMAS ELA Grade 3 district metrics.")
    parser.add_argument("--limit", type=int, default=None, help="Only process first N district codes (debug helper).")
    parser.add_argument(
        "--summary-csv",
        default=str(SUMMARY_SOURCE_CSV),
        help="Local CMAS summary CSV path. If present, this is used instead of web scraping.",
    )
    parser.add_argument(
        "--force-web",
        action="store_true",
        help="Ignore local summary CSV and force the web scraping path.",
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level (default: INFO).")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(levelname)s: %(message)s")
    run(limit=args.limit, summary_csv=Path(args.summary_csv), force_web=args.force_web)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

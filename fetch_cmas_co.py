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
import logging
import re
import sys
from dataclasses import dataclass
from io import StringIO
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


def extract_district_codes(session: requests.Session) -> list[str]:
    html = fetch_html(session, DISTRICT_CODES_URL, RAW_DIR / "district_codes_page.html")
    codes = sorted(extract_codes_from_tables(html))
    if not codes:
        raise RuntimeError("No district codes found on official district code page.")
    logging.info("Found %d district codes", len(codes))
    return codes


def to_float_or_none(value: object) -> float | None:
    if value is None:
        return None
    s = str(value).strip().replace("%", "").replace(",", "")
    if not s or s in {"--", "*", "n<16", "N/A", "NA", "nan", "None"}:
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

    years = list(years)
    if not years:
        return None
    return max(years, key=key)


def extract_district_name(soup: BeautifulSoup, district_code: str) -> str | None:
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    for candidate in [
        soup.select_one("h1"),
        soup.select_one("h2"),
        soup.select_one("meta[property='og:title']"),
    ]:
        if not candidate:
            continue
        if candidate.name == "meta":
            text = candidate.get("content", "").strip()
        else:
            text = candidate.get_text(" ", strip=True)
        if text:
            return re.sub(r"\s+", " ", text)

    if title:
        text = re.sub(r"\s+", " ", title)
        text = re.sub(r"\bCMAS\b.*$", "", text, flags=re.IGNORECASE).strip(" -|")
        if text and text != district_code:
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


def run(limit: int | None = None) -> Path:
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
    parser.add_argument("--log-level", default="INFO", help="Logging level (default: INFO).")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(levelname)s: %(message)s")
    run(limit=args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

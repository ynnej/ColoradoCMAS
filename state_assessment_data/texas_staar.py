from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path

import pandas as pd
import requests

from .common import clean_number, ensure_parent, normalize_code, write_json

SOURCE_PAGE_URL = "https://rptsvr1.tea.texas.gov/perfreport/tapr/2024/Basic%20Download/DownloadSelData.html"
SOURCE_DOWNLOAD_URL = "https://rptsvr1.tea.texas.gov/cgi/sas/broker/DSTAAR_G"
RAW_RELATIVE_PATH = Path("datasets/tx/staar/2023_2024/raw/2023_24_tapr_district_staar_grade3_all_groups.csv")
PROCESSED_RELATIVE_PATH = Path("datasets/tx/staar/2023_2024/processed/staar_2024_district_grade3_all_students.csv")
METADATA_RELATIVE_PATH = Path("datasets/tx/staar/2023_2024/metadata/source.json")


def _download_payload() -> list[tuple[str, str]]:
    return [
        ("_service", "marykay"),
        ("year4", "2024"),
        ("year2", ""),
        ("prgopt", "2024/tapr/Basic Download/xplore/getdata.sas"),
        ("_program", "perfrept.perfmast.sas"),
        ("dsname", "DSTAAR_GR3"),
        ("sumlev", "D"),
        ("_debug", "0"),
        ("format", "XLS"),
        ("dist0", "999999"),
        ("_saveas", "DSTAAR_G"),
        ("datafmt", "C"),
        ("key", "IDENT "),
        ("key", "03ARE1S24 "),
        ("key", "03ARE1224 "),
        ("key", "03ARE1324 "),
        ("key", "03AMA1S24 "),
        ("key", "03AMA1224 "),
        ("key", "03AMA1324 "),
    ]

def _copy_or_download_raw(repo_root: Path, session: requests.Session, raw_csv: Path | None) -> Path:
    destination = repo_root / RAW_RELATIVE_PATH
    ensure_parent(destination)
    if raw_csv is not None:
        source = raw_csv.resolve()
        if source != destination.resolve():
            shutil.copyfile(source, destination)
        return destination

    response = session.post(SOURCE_DOWNLOAD_URL, data=_download_payload(), timeout=120)
    response.raise_for_status()
    if not response.text.lstrip().startswith("DISTRICT,"):
        raise RuntimeError("Unexpected response while downloading Texas TAPR STAAR data.")
    destination.write_text(response.text, encoding="utf-8")
    return destination


def build(
    repo_root: Path,
    session: requests.Session,
    raw_csv: Path | None = None,
) -> list[dict[str, str]]:
    raw_csv_path = _copy_or_download_raw(repo_root, session, raw_csv)
    raw_df = pd.read_csv(raw_csv_path, dtype=str)

    processed = pd.DataFrame(
        {
            "state": "TX",
            "program": "STAAR",
            "school_year": "2023-2024",
            "reporting_year": 2024,
            "district_code": raw_df["DISTRICT"].map(lambda value: normalize_code(value, 6)),
            "district_name": raw_df["DISTNAME"].astype(str).str.strip(),
            "grade": "03",
            "reading_approaches_grade_level_rate_2024": pd.to_numeric(
                raw_df["DDA03ARE1S24R"].map(clean_number), errors="coerce"
            ).astype("Int64"),
            "reading_meets_grade_level_rate_2024": pd.to_numeric(
                raw_df["DDA03ARE1224R"].map(clean_number), errors="coerce"
            ).astype("Int64"),
            "reading_masters_grade_level_rate_2024": pd.to_numeric(
                raw_df["DDA03ARE1324R"].map(clean_number), errors="coerce"
            ).astype("Int64"),
            "math_approaches_grade_level_rate_2024": pd.to_numeric(
                raw_df["DDA03AMA1S24R"].map(clean_number), errors="coerce"
            ).astype("Int64"),
            "math_meets_grade_level_rate_2024": pd.to_numeric(
                raw_df["DDA03AMA1224R"].map(clean_number), errors="coerce"
            ).astype("Int64"),
            "math_masters_grade_level_rate_2024": pd.to_numeric(
                raw_df["DDA03AMA1324R"].map(clean_number), errors="coerce"
            ).astype("Int64"),
        }
    )

    processed_output_path = repo_root / PROCESSED_RELATIVE_PATH
    ensure_parent(processed_output_path)
    processed.to_csv(processed_output_path, index=False)

    metadata = {
        "assessment_program": "STAAR",
        "build_date": dt.date.today().isoformat(),
        "dataset_selector": "DSTAAR_GR3",
        "notes": [
            "Texas TAPR district-level selected-data export for STAAR Grade 3.",
            "The raw download contains all published student-group columns for the selected Grade 3 reading and math measures.",
            "The processed file keeps the all-students district-level rates for reading and math.",
        ],
        "outputs": {
            "district_grade3_all_students_csv": str(PROCESSED_RELATIVE_PATH),
            "raw_district_grade3_all_groups_csv": str(RAW_RELATIVE_PATH),
        },
        "row_counts": {
            "district_grade3_all_groups": int(len(raw_df)),
            "district_grade3_all_students": int(len(processed)),
        },
        "source_download_url": SOURCE_DOWNLOAD_URL,
        "source_page_url": SOURCE_PAGE_URL,
        "state": "TX",
        "state_name": "Texas",
    }
    write_json(repo_root / METADATA_RELATIVE_PATH, metadata)

    return [
        {
            "state": "TX",
            "state_name": "Texas",
            "program": "STAAR",
            "reporting_period": "2023-2024",
            "kind": "raw",
            "granularity": "district",
            "description": "District Grade 3 STAAR raw TAPR export with all published student-group columns.",
            "path": str(RAW_RELATIVE_PATH),
            "source_url": SOURCE_PAGE_URL,
        },
        {
            "state": "TX",
            "state_name": "Texas",
            "program": "STAAR",
            "reporting_period": "2023-2024",
            "kind": "processed",
            "granularity": "district",
            "description": "District Grade 3 STAAR all-students reading and math rates.",
            "path": str(PROCESSED_RELATIVE_PATH),
            "source_url": SOURCE_PAGE_URL,
        },
    ]

from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path

import pandas as pd
import requests

from .common import clean_number, ensure_parent, normalize_code, normalize_grade, slugify_column, write_json

SOURCE_PAGE_URL = "https://ed.cde.state.co.us/assessment/cmas-dataandresults-2025"
SOURCE_DOWNLOAD_URL = (
    "https://resources.finalsite.net/files/t_file_download/v1776115348/"
    "cdestatecous/rrkmbmijrknlrhuvzk4e/2025CMASMathELACSLADistrictandSchoolSummaryAchievementResults.xlsx"
)

RAW_RELATIVE_PATH = Path("datasets/co/cmas/2025/raw/2025_cmas_math_ela_district_school_overall.xlsx")
OVERALL_RELATIVE_PATH = Path("datasets/co/cmas/2025/processed/cmas_2025_district_school_overall.csv")
GRADE3_RELATIVE_PATH = Path("datasets/co/cmas/2025/processed/cmas_2025_district_grade3_ela.csv")
METADATA_RELATIVE_PATH = Path("datasets/co/cmas/2025/metadata/source.json")


def _copy_or_download_raw(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> Path:
    destination = repo_root / RAW_RELATIVE_PATH
    ensure_parent(destination)
    if raw_workbook is not None:
        source = raw_workbook.resolve()
        if source != destination.resolve():
            shutil.copyfile(source, destination)
        return destination

    response = session.get(SOURCE_DOWNLOAD_URL, timeout=120)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination


def _rename_columns(columns: list[object]) -> list[str]:
    rename_map = {
        "Level": "level",
        "District Code": "district_code",
        "District Name": "district_name",
        "School Code": "school_code",
        "School Name": "school_name",
        "Content": "content",
        "Grade": "grade",
        "Number of Total Records": "number_of_total_records",
        "Number of Valid Scores": "number_of_valid_scores",
        "Number of No Scores": "number_of_no_scores",
        "Participation Rate 2025": "participation_rate_2025",
        "Participation Rate 2024": "participation_rate_2024",
        "Participation Rate 2023": "participation_rate_2023",
        "Mean Scale Score": "mean_scale_score",
        "Standard Deviation": "standard_deviation",
        "Number Did Not Yet Meet Expectations": "number_did_not_yet_meet_expectations",
        "Percent Did Not Yet Meet Expectations": "percent_did_not_yet_meet_expectations",
        "Number Partially Met Expectations": "number_partially_met_expectations",
        "Percent Partially Met Expectations": "percent_partially_met_expectations",
        "Number Approached Expectations": "number_approached_expectations",
        "Percent Approached Expectations": "percent_approached_expectations",
        "Number Met Expectations": "number_met_expectations",
        "Percent Met Expectations": "percent_met_expectations",
        "Number Exceeded Expectations": "number_exceeded_expectations",
        "Percent Exceeded Expectations": "percent_exceeded_expectations",
        "Number Met or Exceeded Expectations": "number_met_or_exceeded_expectations",
        "2025": "percent_met_or_exceeded_expectations_2025",
        2024: "percent_met_or_exceeded_expectations_2024",
        2023: "percent_met_or_exceeded_expectations_2023",
        "Change\n2025-2024": "change_percent_met_or_exceeded_expectations_2025_2024",
        "Congressional\nDistrict": "congressional_district",
    }
    renamed: list[str] = []
    for column in columns:
        renamed.append(rename_map.get(column, slugify_column(column)))
    return renamed


def _load_overall_dataframe(raw_workbook_path: Path) -> pd.DataFrame:
    df = pd.read_excel(raw_workbook_path, header=17, dtype=str).dropna(how="all").copy()
    df.columns = _rename_columns(df.columns.tolist())

    if "district_code" in df.columns:
        df["district_code"] = df["district_code"].apply(lambda value: normalize_code(value, 4))
    if "school_code" in df.columns:
        df["school_code"] = df["school_code"].apply(lambda value: normalize_code(value, 4))
    if "grade" in df.columns:
        df["grade"] = df["grade"].apply(normalize_grade)

    count_columns = [
        "number_of_total_records",
        "number_of_valid_scores",
        "number_of_no_scores",
        "number_did_not_yet_meet_expectations",
        "number_partially_met_expectations",
        "number_approached_expectations",
        "number_met_expectations",
        "number_exceeded_expectations",
        "number_met_or_exceeded_expectations",
    ]
    rate_columns = [
        "participation_rate_2025",
        "participation_rate_2024",
        "participation_rate_2023",
        "mean_scale_score",
        "standard_deviation",
        "percent_did_not_yet_meet_expectations",
        "percent_partially_met_expectations",
        "percent_approached_expectations",
        "percent_met_expectations",
        "percent_exceeded_expectations",
        "percent_met_or_exceeded_expectations_2025",
        "percent_met_or_exceeded_expectations_2024",
        "percent_met_or_exceeded_expectations_2023",
        "change_percent_met_or_exceeded_expectations_2025_2024",
    ]

    for column in count_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column].map(clean_number), errors="coerce").astype("Int64")
    for column in rate_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column].map(clean_number), errors="coerce")

    return df


def build(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None = None,
) -> list[dict[str, str]]:
    raw_workbook_path = _copy_or_download_raw(repo_root, session, raw_workbook)
    df = _load_overall_dataframe(raw_workbook_path)

    district_school = df[df["level"].fillna("").str.upper().isin({"DISTRICT", "SCHOOL"})].copy()
    overall_output_path = repo_root / OVERALL_RELATIVE_PATH
    ensure_parent(overall_output_path)
    district_school.to_csv(overall_output_path, index=False)

    district_grade3 = district_school[
        district_school["level"].fillna("").str.upper().eq("DISTRICT")
        & district_school["content"].fillna("").str.lower().eq("english language arts")
        & district_school["grade"].fillna("").eq("03")
    ].copy()
    district_grade3.insert(0, "state", "CO")
    district_grade3.insert(1, "program", "CMAS")
    district_grade3.insert(2, "reporting_year", 2025)
    district_grade3_output = district_grade3[
        [
            "state",
            "program",
            "reporting_year",
            "district_code",
            "district_name",
            "content",
            "grade",
            "number_of_valid_scores",
            "participation_rate_2025",
            "percent_met_or_exceeded_expectations_2025",
            "percent_met_or_exceeded_expectations_2024",
            "percent_met_or_exceeded_expectations_2023",
            "change_percent_met_or_exceeded_expectations_2025_2024",
            "number_met_or_exceeded_expectations",
        ]
    ].rename(columns={"content": "subject"})
    grade3_output_path = repo_root / GRADE3_RELATIVE_PATH
    ensure_parent(grade3_output_path)
    district_grade3_output.to_csv(grade3_output_path, index=False)

    metadata = {
        "assessment_program": "CMAS",
        "build_date": dt.date.today().isoformat(),
        "notes": [
            "Colorado public district and school achievement workbook for math and ELA.",
            "This repo stores both the full normalized district/school table and a filtered district Grade 3 ELA slice.",
        ],
        "outputs": {
            "district_grade3_ela_csv": str(GRADE3_RELATIVE_PATH),
            "district_school_overall_csv": str(OVERALL_RELATIVE_PATH),
            "raw_workbook": str(RAW_RELATIVE_PATH),
        },
        "row_counts": {
            "district_grade3_ela": int(len(district_grade3_output)),
            "district_school_overall": int(len(district_school)),
        },
        "source_download_url": SOURCE_DOWNLOAD_URL,
        "source_page_url": SOURCE_PAGE_URL,
        "state": "CO",
        "state_name": "Colorado",
    }
    write_json(repo_root / METADATA_RELATIVE_PATH, metadata)

    return [
        {
            "state": "CO",
            "state_name": "Colorado",
            "program": "CMAS",
            "reporting_period": "2025",
            "kind": "raw",
            "granularity": "district+school",
            "description": "Official CMAS math and ELA district/school overall results workbook.",
            "path": str(RAW_RELATIVE_PATH),
            "source_url": SOURCE_DOWNLOAD_URL,
        },
        {
            "state": "CO",
            "state_name": "Colorado",
            "program": "CMAS",
            "reporting_period": "2025",
            "kind": "processed",
            "granularity": "district+school",
            "description": "Normalized CMAS district and school overall results.",
            "path": str(OVERALL_RELATIVE_PATH),
            "source_url": SOURCE_DOWNLOAD_URL,
        },
        {
            "state": "CO",
            "state_name": "Colorado",
            "program": "CMAS",
            "reporting_period": "2025",
            "kind": "processed",
            "granularity": "district",
            "description": "District Grade 3 English Language Arts slice with participation and met/exceeded rates.",
            "path": str(GRADE3_RELATIVE_PATH),
            "source_url": SOURCE_DOWNLOAD_URL,
        },
    ]

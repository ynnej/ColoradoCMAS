from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

import pandas as pd
import requests

from .common import ensure_parent, write_json

NAEP_SOURCE_PAGE_URL = "https://www.nationsreportcard.gov/profiles/"
NAEP_SERVICE_URL = "https://www.nationsreportcard.gov/NDEDataService/ChartHandler.aspx"
NAEP_QUERY_URL = (
    "https://www.nationsreportcard.gov/NDEDataService/ChartHandler.aspx"
    "?type=sp_state_map_datatable"
    "&subject=RED"
    "&cohort=1"
    "&year=2024R3"
    "&wantse=false"
    "&wantextdecplaces=false"
)
NAEP_RAW_RELATIVE_PATH = Path("datasets/naep/2024/raw/naep_2024_grade4_reading_state_map_datatable.json")

LOOKER_MINIMAL_RELATIVE_PATH = Path("datasets/summary/state_assessment_vs_naep_looker_minimal.csv")
LOOKER_ENRICHED_RELATIVE_PATH = Path("datasets/summary/state_assessment_vs_naep_looker_enriched.csv")
LOOKER_METADATA_RELATIVE_PATH = Path("datasets/summary/metadata/state_assessment_vs_naep_looker_sources.json")
CATALOG_RELATIVE_PATH = Path("datasets/catalog.csv")


def _copy_or_download_naep_json(
    repo_root: Path,
    session: requests.Session,
    local_override: Path | None,
) -> Path:
    destination = repo_root / NAEP_RAW_RELATIVE_PATH
    ensure_parent(destination)

    if local_override is not None:
        source = local_override.resolve()
        if source != destination.resolve():
            shutil.copyfile(source, destination)
        return destination

    if destination.exists():
        return destination

    response = session.get(
        NAEP_SERVICE_URL,
        params={
            "type": "sp_state_map_datatable",
            "subject": "RED",
            "cohort": "1",
            "year": "2024R3",
            "wantse": "false",
            "wantextdecplaces": "false",
        },
        timeout=120,
    )
    response.raise_for_status()
    destination.write_text(response.text, encoding="utf-8")
    return destination


def _update_catalog(repo_root: Path, new_entries: list[dict[str, str]]) -> None:
    catalog_path = repo_root / CATALOG_RELATIVE_PATH
    base_columns = [
        "state",
        "state_name",
        "program",
        "reporting_period",
        "kind",
        "granularity",
        "description",
        "path",
        "source_url",
    ]

    existing = pd.read_csv(catalog_path, dtype=str) if catalog_path.exists() else pd.DataFrame(columns=base_columns)
    additions = pd.DataFrame(new_entries, columns=base_columns)
    combined = pd.concat([existing, additions], ignore_index=True)
    combined = combined.drop_duplicates(subset=["path"], keep="last")
    combined = combined.sort_values(by=["state", "program", "reporting_period", "kind", "path"], kind="stable")
    ensure_parent(catalog_path)
    combined.to_csv(catalog_path, index=False)


def _metric_suffix(label: str, source_bin_structure: str) -> str:
    if source_bin_structure == "published_cumulative_thresholds":
        return " (Published Source Bin)"
    if source_bin_structure == "published_pass_rate_breakout":
        return " (Published Source Bin)"
    if source_bin_structure == "published_proficiency_only":
        return " (Public Reference)"
    if source_bin_structure == "federal_proficiency_only_proxy":
        return " (Federal Proxy Source)"
    return ""


def _display_metric_label(label: str, source_bin_structure: str) -> str:
    base_label = label.strip()
    if not base_label:
        return _metric_suffix(base_label, source_bin_structure).strip()
    if base_label.lower().startswith("percent "):
        return f"{base_label}{_metric_suffix(base_label, source_bin_structure)}"
    return f"Percent {base_label}{_metric_suffix(base_label, source_bin_structure)}"


def _format_pct(value: object) -> float | None:
    if value is None or value == "":
        return None
    return round(float(value), 2)


def build_looker_state_naep_comparison(
    repo_root: Path,
    session: requests.Session,
    below_basic_path: Path,
    tiers_path: Path,
    published_reference_path: Path,
    naep_raw_json: Path | None = None,
) -> dict[str, Path]:
    naep_raw_path = _copy_or_download_naep_json(repo_root, session, naep_raw_json)

    below_basic_df = pd.read_csv(below_basic_path)
    tiers_df = pd.read_csv(tiers_path)
    published_reference_df = pd.read_csv(published_reference_path)

    state_name_map: dict[str, str] = {}
    for _, row in below_basic_df.iterrows():
        state_name_map[str(row["state"])] = str(row["state_name"])
    for _, row in published_reference_df.iterrows():
        state_name_map[str(row["state"])] = str(row["state_name"])

    naep_payload = json.loads(naep_raw_path.read_text(encoding="utf-8"))
    naep_rows = {
        row["JurisdictionCode"]: row
        for row in naep_payload["result"]["StateMap_DataTableData"]["Statedata"]
    }
    national_public_row = naep_rows["NP"]

    rows: list[dict[str, object]] = []

    def add_row(
        *,
        state_code: str,
        state_name: str,
        year: int,
        school_year: str,
        grade: int,
        subject: str,
        source: str,
        assessment: str,
        metric: str,
        value: float | None,
        metric_family: str,
        comparison_role: str,
        jurisdiction_of_measure: str,
        jurisdiction_of_measure_name: str,
        source_value_kind: str,
        benchmark_label: str,
        source_url: str,
        source_page_url: str,
        notes: str,
        detail_order: int = 0,
    ) -> None:
        if value is None:
            return
        rows.append(
            {
                "state": state_name,
                "state_code": state_code,
                "year": year,
                "school_year": school_year,
                "grade": grade,
                "subject": subject,
                "source": source,
                "assessment": assessment,
                "metric": metric,
                "value": round(float(value), 2),
                "metric_family": metric_family,
                "comparison_role": comparison_role,
                "jurisdiction_of_measure": jurisdiction_of_measure,
                "jurisdiction_of_measure_name": jurisdiction_of_measure_name,
                "source_value_kind": source_value_kind,
                "benchmark_label": benchmark_label,
                "source_url": source_url,
                "source_page_url": source_page_url,
                "notes": notes,
                "detail_order": detail_order,
            }
        )

    for _, row in below_basic_df.sort_values(by=["state"], kind="stable").iterrows():
        add_row(
            state_code=str(row["state"]),
            state_name=str(row["state_name"]),
            year=int(row["administration_year"]),
            school_year=str(row["school_year"]),
            grade=int(str(row["grade"])),
            subject="ELA",
            source=str(row["assessment"]),
            assessment=str(row["assessment"]),
            metric="Percent in Below-Basic Analog Tier",
            value=_format_pct(row["below_basic_analog_pct"]),
            metric_family="state_below_basic_analog",
            comparison_role="state_assessment",
            jurisdiction_of_measure=str(row["state"]),
            jurisdiction_of_measure_name=str(row["state_name"]),
            source_value_kind="below_basic_analog",
            benchmark_label=str(row["below_basic_analog_label"]),
            source_url=str(row["source_url"]),
            source_page_url=str(row["source_page_url"]),
            notes=str(row["source_notes"]),
            detail_order=0,
        )

    for _, row in tiers_df.sort_values(by=["state", "tier_rank"], kind="stable").iterrows():
        add_row(
            state_code=str(row["state"]),
            state_name=state_name_map[str(row["state"])],
            year=int(row["administration_year"]),
            school_year=str(row["school_year"]),
            grade=int(str(row["grade"])),
            subject="ELA",
            source=str(row["assessment"]),
            assessment=str(row["assessment"]),
            metric=f"Percent {row['tier_label']}",
            value=_format_pct(row["pct_students"]),
            metric_family="state_exact_tier",
            comparison_role="state_assessment",
            jurisdiction_of_measure=str(row["state"]),
            jurisdiction_of_measure_name=state_name_map[str(row["state"])],
            source_value_kind=str(row["source_value_kind"]),
            benchmark_label=str(row["tier_label"]),
            source_url=str(row["source_url"]),
            source_page_url=str(row["source_page_url"]),
            notes=str(row["notes"]),
            detail_order=int(row["tier_rank"]),
        )

    for _, row in published_reference_df.sort_values(by=["state"], kind="stable").iterrows():
        source_bin_structure = str(row["source_bin_structure"])
        if source_bin_structure in {"published_exact_tiers", "published_counts_by_exact_tier"}:
            continue

        for bin_number in range(1, 6):
            label = row.get(f"source_bin_{bin_number}_label")
            value = row.get(f"source_bin_{bin_number}_pct")
            if pd.isna(label) or str(label).strip() == "":
                continue
            add_row(
                state_code=str(row["state"]),
                state_name=str(row["state_name"]),
                year=int(row["administration_year"]),
                school_year=str(row["school_year"]),
                grade=int(str(row["grade"])),
                subject="ELA",
                source=str(row["assessment"]),
                assessment=str(row["assessment"]),
                metric=_display_metric_label(str(label), source_bin_structure),
                value=_format_pct(value),
                metric_family="state_published_source_bin",
                comparison_role="state_assessment_reference",
                jurisdiction_of_measure=str(row["state"]),
                jurisdiction_of_measure_name=str(row["state_name"]),
                source_value_kind=source_bin_structure,
                benchmark_label=str(label),
                source_url=str(row["source_url"]),
                source_page_url=str(row["source_page_url"]),
                notes=str(row["notes"]),
                detail_order=bin_number,
            )

    for state_code, state_name in sorted(state_name_map.items()):
        naep_state_row = naep_rows.get(state_code)
        if naep_state_row is not None:
            add_row(
                state_code=state_code,
                state_name=state_name,
                year=2024,
                school_year="2024",
                grade=4,
                subject="Reading",
                source="NAEP (State)",
                assessment="NAEP",
                metric="Percent Below Basic",
                value=100.0 - float(naep_state_row["AB_FP"]),
                metric_family="naep_below_basic",
                comparison_role="naep_state",
                jurisdiction_of_measure=state_code,
                jurisdiction_of_measure_name=str(naep_state_row["Jurisdiction"]),
                source_value_kind="derived_from_pct_at_or_above_basic",
                benchmark_label="State NAEP",
                source_url=NAEP_QUERY_URL,
                source_page_url=NAEP_SOURCE_PAGE_URL,
                notes="Derived as 100 minus NAEP percent at or above Basic from the official 2024 Grade 4 Reading state table.",
                detail_order=0,
            )

        add_row(
            state_code=state_code,
            state_name=state_name,
            year=2024,
            school_year="2024",
            grade=4,
            subject="Reading",
            source="NAEP (National Public)",
            assessment="NAEP",
            metric="Percent Below Basic",
            value=100.0 - float(national_public_row["AB_FP"]),
            metric_family="naep_below_basic",
            comparison_role="naep_national_public_benchmark",
            jurisdiction_of_measure="NP",
            jurisdiction_of_measure_name=str(national_public_row["Jurisdiction"]),
            source_value_kind="derived_from_pct_at_or_above_basic",
            benchmark_label="National Public",
            source_url=NAEP_QUERY_URL,
            source_page_url=NAEP_SOURCE_PAGE_URL,
            notes=(
                "Repeated National Public NAEP benchmark row so a simple state filter in Looker Studio "
                "still shows the national comparison without a join."
            ),
            detail_order=0,
        )

    enriched_df = pd.DataFrame(rows)
    role_order = {
        "naep_national_public_benchmark": 1,
        "naep_state": 2,
        "state_assessment": 3,
        "state_assessment_reference": 4,
    }
    family_order = {
        "naep_below_basic": 1,
        "state_below_basic_analog": 2,
        "state_exact_tier": 3,
        "state_published_source_bin": 4,
    }
    enriched_df["source_order"] = enriched_df["comparison_role"].map(role_order).fillna(99)
    enriched_df["metric_order"] = enriched_df["metric_family"].map(family_order).fillna(99)
    enriched_df = enriched_df.sort_values(
        by=["state", "year", "source_order", "metric_order", "detail_order", "metric"],
        kind="stable",
    )

    enriched_output_path = repo_root / LOOKER_ENRICHED_RELATIVE_PATH
    ensure_parent(enriched_output_path)
    enriched_df.to_csv(enriched_output_path, index=False)

    minimal_df = enriched_df[
        ["state", "year", "grade", "subject", "source", "assessment", "metric", "value"]
    ].copy()
    minimal_output_path = repo_root / LOOKER_MINIMAL_RELATIVE_PATH
    ensure_parent(minimal_output_path)
    minimal_df.to_csv(minimal_output_path, index=False)

    metadata = {
        "build_date": dt.date.today().isoformat(),
        "description": (
            "Looker-ready long tables combining state assessment Grade 3 ELA rows with 2024 NAEP Grade 4 Reading "
            "below-basic comparison rows."
        ),
        "outputs": {
            "looker_minimal_csv": str(LOOKER_MINIMAL_RELATIVE_PATH),
            "looker_enriched_csv": str(LOOKER_ENRICHED_RELATIVE_PATH),
            "naep_raw_json": str(NAEP_RAW_RELATIVE_PATH),
        },
        "naep_logic": {
            "metric": "Percent Below Basic",
            "derivation": "100 - percent at or above Basic from the official NAEP 2024 Grade 4 Reading state data table.",
            "repeated_national_benchmark": True,
        },
        "state_assessment_logic": {
            "below_basic_analog_rows": "Use the strict below-basic analog rows already defined in statewide_grade3_ela_below_basic_analog.csv.",
            "exact_tier_rows": "Use exact statewide Grade 3 ELA tiers where available.",
            "published_reference_rows": (
                "Add source-bin rows only when they provide additional context beyond exact tiers, such as Texas published thresholds "
                "or West Virginia's proficiency-only public reference."
            ),
        },
        "sources": {
            "naep_query_url": NAEP_QUERY_URL,
            "naep_source_page_url": NAEP_SOURCE_PAGE_URL,
        },
    }
    metadata_output_path = repo_root / LOOKER_METADATA_RELATIVE_PATH
    write_json(metadata_output_path, metadata)

    _update_catalog(
        repo_root,
        [
            {
                "state": "MULTI",
                "state_name": "Multiple States",
                "program": "NAEP",
                "reporting_period": "2024",
                "kind": "raw",
                "granularity": "state+national",
                "description": "Raw NAEP 2024 Grade 4 Reading state data table used for Looker comparison rows.",
                "path": str(NAEP_RAW_RELATIVE_PATH),
                "source_url": NAEP_QUERY_URL,
            },
            {
                "state": "MULTI",
                "state_name": "Multiple States",
                "program": "LOOKER_STATE_ASSESSMENT_NAEP",
                "reporting_period": "2023-2025 mixed",
                "kind": "processed",
                "granularity": "state",
                "description": "Minimal Looker-ready long table for state assessment and NAEP comparison rows.",
                "path": str(LOOKER_MINIMAL_RELATIVE_PATH),
                "source_url": "",
            },
            {
                "state": "MULTI",
                "state_name": "Multiple States",
                "program": "LOOKER_STATE_ASSESSMENT_NAEP",
                "reporting_period": "2023-2025 mixed",
                "kind": "processed",
                "granularity": "state",
                "description": "Enriched Looker-ready long table with state assessment and NAEP comparison metadata columns.",
                "path": str(LOOKER_ENRICHED_RELATIVE_PATH),
                "source_url": "",
            },
        ],
    )

    return {
        "looker_minimal": minimal_output_path,
        "looker_enriched": enriched_output_path,
        "looker_metadata": metadata_output_path,
        "naep_raw_json": repo_root / NAEP_RAW_RELATIVE_PATH,
    }

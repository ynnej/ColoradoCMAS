#!/usr/bin/env python3
"""Build a small, readable cross-state Grade 3 ELA tier comparison."""

from __future__ import annotations

import argparse
from pathlib import Path

from state_assessment_data.common import build_session
from state_assessment_data.looker_state_naep import build_looker_state_naep_comparison
from state_assessment_data.statewide_grade3_ela import build_statewide_grade3_ela


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build statewide Grade 3 ELA tier comparison files.")
    parser.add_argument(
        "--ak-raw-pdf",
        type=Path,
        default=None,
        help="Optional local Alaska 2025 assessment brief PDF path.",
    )
    parser.add_argument(
        "--ar-raw-workbook",
        type=Path,
        default=None,
        help="Optional local Arkansas ATLAS statewide summary workbook path.",
    )
    parser.add_argument(
        "--ca-raw-workbook",
        type=Path,
        default=None,
        help="Optional local California CAASPP Grade 3 ELA workbook path.",
    )
    parser.add_argument(
        "--co-raw-workbook",
        type=Path,
        default=None,
        help="Optional local Colorado CMAS workbook path.",
    )
    parser.add_argument(
        "--ct-raw-json",
        type=Path,
        default=None,
        help="Optional local Connecticut EdSight Grade 3 ELA saved extract path.",
    )
    parser.add_argument(
        "--dc-raw-workbook",
        type=Path,
        default=None,
        help="Optional local District of Columbia DC CAPE statewide results workbook path.",
    )
    parser.add_argument(
        "--fl-raw-workbook",
        type=Path,
        default=None,
        help="Optional local Florida FAST Grade 3 ELA workbook path.",
    )
    parser.add_argument(
        "--ga-raw-workbook",
        type=Path,
        default=None,
        help="Optional local Georgia Milestones statewide Grade 3 workbook path.",
    )
    parser.add_argument(
        "--in-raw-workbook",
        type=Path,
        default=None,
        help="Optional local Indiana ILEARN statewide summary workbook path.",
    )
    parser.add_argument(
        "--la-raw-workbook",
        type=Path,
        default=None,
        help="Optional local Louisiana LEAP State LEA achievement workbook path.",
    )
    parser.add_argument(
        "--ma-raw-html",
        type=Path,
        default=None,
        help="Optional local Massachusetts state-profile achievement-level HTML path.",
    )
    parser.add_argument(
        "--md-raw-json",
        type=Path,
        default=None,
        help="Optional local Maryland Report Card Grade 3 MCAP ELA JSON response path.",
    )
    parser.add_argument(
        "--nc-raw-workbook",
        type=Path,
        default=None,
        help="Optional local North Carolina statewide assessment workbook path.",
    )
    parser.add_argument(
        "--nj-raw-workbook",
        type=Path,
        default=None,
        help="Optional local New Jersey NJSLA Grade 3 ELA workbook path.",
    )
    parser.add_argument(
        "--oh-raw-workbook",
        type=Path,
        default=None,
        help="Optional local Ohio Title 1 Proficiency by Grade workbook path.",
    )
    parser.add_argument(
        "--pa-raw-html",
        type=Path,
        default=None,
        help="Optional local Pennsylvania assessment reporting HTML path.",
    )
    parser.add_argument(
        "--ri-raw-json",
        type=Path,
        default=None,
        help="Optional local Rhode Island ADP Grade 3 ELA saved extract path.",
    )
    parser.add_argument(
        "--tn-raw-workbook",
        type=Path,
        default=None,
        help="Optional local Tennessee state assessment workbook path.",
    )
    parser.add_argument(
        "--tx-raw-workbook",
        type=Path,
        default=None,
        help="Optional local Texas statewide TAPR Grade 3 STAAR workbook path.",
    )
    parser.add_argument(
        "--va-raw-html",
        type=Path,
        default=None,
        help="Optional local Virginia state quality profile HTML path.",
    )
    parser.add_argument(
        "--wa-raw-csv",
        type=Path,
        default=None,
        help="Optional local Washington assessment CSV or state extract path.",
    )
    parser.add_argument(
        "--wi-raw-zip",
        type=Path,
        default=None,
        help="Optional local Wisconsin Forward certified zip path.",
    )
    parser.add_argument(
        "--naep-raw-json",
        type=Path,
        default=None,
        help="Optional local NAEP 2024 Grade 4 Reading state table JSON path.",
    )
    parser.add_argument(
        "--naep-achievement-json",
        type=Path,
        default=None,
        help="Optional local NAEP 2024 Grade 4 Reading achievement-level JSON path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    session = build_session(user_agent="StatewideGrade3ELATiers/1.0")
    outputs = build_statewide_grade3_ela(
        repo_root=repo_root,
        session=session,
        ak_raw_pdf=args.ak_raw_pdf,
        ar_raw_workbook=args.ar_raw_workbook,
        ca_raw_workbook=args.ca_raw_workbook,
        co_raw_workbook=args.co_raw_workbook,
        ct_raw_json=args.ct_raw_json,
        dc_raw_workbook=args.dc_raw_workbook,
        fl_raw_workbook=args.fl_raw_workbook,
        ga_raw_workbook=args.ga_raw_workbook,
        in_raw_workbook=args.in_raw_workbook,
        la_raw_workbook=args.la_raw_workbook,
        ma_raw_html=args.ma_raw_html,
        md_raw_json=args.md_raw_json,
        nc_raw_workbook=args.nc_raw_workbook,
        nj_raw_workbook=args.nj_raw_workbook,
        oh_raw_workbook=args.oh_raw_workbook,
        pa_raw_html=args.pa_raw_html,
        ri_raw_json=args.ri_raw_json,
        tn_raw_workbook=args.tn_raw_workbook,
        tx_raw_workbook=args.tx_raw_workbook,
        va_raw_html=args.va_raw_html,
        wa_raw_csv=args.wa_raw_csv,
        wi_raw_zip=args.wi_raw_zip,
    )
    looker_outputs = build_looker_state_naep_comparison(
        repo_root=repo_root,
        session=session,
        below_basic_path=outputs["below_basic_analog"],
        tiers_path=outputs["cross_state_tiers"],
        published_reference_path=outputs["published_reference_bins"],
        naep_raw_json=args.naep_raw_json,
        naep_achievement_json=args.naep_achievement_json,
    )
    outputs = {**outputs, **looker_outputs}

    for label, path in outputs.items():
        print(f"{label}: {path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

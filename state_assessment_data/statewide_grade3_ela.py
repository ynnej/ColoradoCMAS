from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import zipfile
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests

from .common import clean_number, ensure_parent, write_json

CO_SOURCE_PAGE_URL = "https://ed.cde.state.co.us/assessment/cmas-dataandresults-2025"
CO_SOURCE_DOWNLOAD_URL = (
    "https://resources.finalsite.net/files/t_file_download/v1776115348/"
    "cdestatecous/rrkmbmijrknlrhuvzk4e/2025CMASMathELACSLADistrictandSchoolSummaryAchievementResults.xlsx"
)
CO_RAW_RELATIVE_PATH = Path("datasets/co/cmas/2025/raw/2025_cmas_math_ela_district_school_overall.xlsx")
CO_OUTPUT_RELATIVE_PATH = Path("datasets/co/cmas/2025/processed/cmas_2025_statewide_grade3_ela_tiers.csv")

CT_SOURCE_PAGE_URL = "https://public-edsight.ct.gov/performance/smarter-balanced-achievement-participation"
CT_SOURCE_DOWNLOAD_URL = (
    "https://edsight.ct.gov/SASStoredProcess/guest?_grade=3&_year=2024-25"
    "&_district=State+of+Connecticut&_school=&_subject=ELA&_subgroup=All+Students"
    "&_program=%2FCTDOE%2FEdSight%2FRelease%2FReporting%2FPublic%2FReports%2FStoredProcesses%2FSmarterBalancedAssessmentReport_SiteCore"
    "&_select=Submit"
)
CT_RAW_RELATIVE_PATH = Path(
    "datasets/ct/smarter_balanced/2024_2025/raw/edsight_2025_state_grade3_ela_all_students.json"
)
CT_OUTPUT_RELATIVE_PATH = Path(
    "datasets/ct/smarter_balanced/2024_2025/processed/smarter_balanced_2025_statewide_grade3_ela_tiers.csv"
)

AK_SOURCE_PAGE_URL = "https://education.alaska.gov/assessment-results/Statewide/StatewideResults?isScience=False&schoolYear=2024-2025"
AK_SOURCE_DOWNLOAD_URL = "https://education.alaska.gov/akassessments/AKAssessment_Brief_2025.pdf"
AK_RAW_RELATIVE_PATH = Path("datasets/ak/ak_star/2024_2025/raw/ak_assessment_brief_2025.pdf")
AK_OUTPUT_RELATIVE_PATH = Path("datasets/ak/ak_star/2024_2025/processed/ak_star_2025_statewide_grade3_ela_tiers.csv")

AR_SOURCE_PAGE_URL = "https://dese.ade.arkansas.gov/Offices/public-school-accountability/assessment-test-scores/2025"
AR_SOURCE_DOWNLOAD_URL = "https://dese.ade.arkansas.gov/Files/Atlas_Summary_Post-Corrections_Scores_Spring_2025_PSA.xlsx"
AR_RAW_RELATIVE_PATH = Path("datasets/ar/atlas/2024_2025/raw/atlas_summary_post_corrections_scores_spring_2025_psa.xlsx")
AR_OUTPUT_RELATIVE_PATH = Path("datasets/ar/atlas/2024_2025/processed/atlas_2025_statewide_grade3_ela_tiers.csv")

CA_SOURCE_PAGE_URL = "https://www.cde.ca.gov/ta/tg/ca/caaspp2025datasummary.asp"
CA_SOURCE_DOWNLOAD_URL = "https://www.cde.ca.gov/ta/tg/ca/documents/elaallall2025.xlsx"
CA_RAW_RELATIVE_PATH = Path("datasets/ca/caaspp/2024_2025/raw/ela_all_all_2025.xlsx")
CA_OUTPUT_RELATIVE_PATH = Path(
    "datasets/ca/caaspp/2024_2025/processed/caaspp_2025_statewide_grade3_ela_public_reference.csv"
)

DE_SOURCE_PAGE_URL = (
    "https://education.delaware.gov/educators/academic-support/standards-and-assessments/"
    "english-and-language-arts/assessments/"
)
DE_SOURCE_DOWNLOAD_URL = "https://data.delaware.gov/api/views/ms6b-mt82/rows.csv?accessType=DOWNLOAD"
DE_OUTPUT_RELATIVE_PATH = Path(
    "datasets/de/dessa/2024_2025/processed/dessa_2025_statewide_grade3_ela_public_reference.csv"
)

DC_SOURCE_PAGE_URL = "https://osse.dc.gov/node/1794106"
DC_SOURCE_DOWNLOAD_URL = (
    "https://app.box.com/index.php?rm=box_download_shared_file"
    "&shared_name=l1fz6ucfcut7q7pg8qzbo3l9ffb19pmm"
    "&file_id=f_1962534999838"
)
DC_RAW_RELATIVE_PATH = Path(
    "datasets/dc/dc_cape/2024_2025/raw/2024_25_public_file_sea_level_dccape_msaa_data_1.xlsx"
)
DC_OUTPUT_RELATIVE_PATH = Path(
    "datasets/dc/dc_cape/2024_2025/processed/dc_cape_2025_statewide_grade3_ela_tiers.csv"
)

FL_SOURCE_PAGE_URL = "https://www.fldoe.org/accountability/assessments/k-12-student-assessment/results/2025.stml"
FL_SOURCE_DOWNLOAD_URL = "https://origin.fldoe.org/core/fileparse.php/5668/urlt/3ELA03SRDSpring25.xls"
FL_DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://origin.fldoe.org/accountability/assessments/k-12-student-assessment/results/2025.stml",
}
FL_RAW_RELATIVE_PATH = Path("datasets/fl/fast/2024_2025/raw/2025_fast_grade3_ela_pm3_state_district.xls")
FL_OUTPUT_RELATIVE_PATH = Path("datasets/fl/fast/2024_2025/processed/fast_2025_statewide_grade3_ela_tiers.csv")

GA_SOURCE_PAGE_URL = "https://gadoe.org/assessment-accountability/georgia-milestones/"
GA_SOURCE_DOWNLOAD_URL = "https://url.gadoe.org/r9zz0"
GA_RAW_RELATIVE_PATH = Path("datasets/ga/georgia_milestones/2024_2025/raw/spring_2025_eog_state_summary.xlsx")
GA_OUTPUT_RELATIVE_PATH = Path(
    "datasets/ga/georgia_milestones/2024_2025/processed/georgia_milestones_2025_statewide_grade3_ela_tiers.csv"
)

IN_SOURCE_PAGE_URL = "https://secure.in.gov/doe/it/data-center-and-reports/"
IN_SOURCE_DOWNLOAD_URL = "https://secure.in.gov/doe/files/ILEARN-2025-Grade3-8-Final-Statewide-Summary_20250714.xlsx"
IN_RAW_RELATIVE_PATH = Path("datasets/in/ilearn/2024_2025/raw/2025_ilearn_grade3_8_statewide_summary.xlsx")
IN_OUTPUT_RELATIVE_PATH = Path("datasets/in/ilearn/2024_2025/processed/ilearn_2025_statewide_grade3_ela_tiers.csv")

KY_SOURCE_PAGE_URL = "https://www.education.ky.gov/AA/Assessments/Pages/KentuckySummativeAssessment-.aspx"
KY_SOURCE_DOWNLOAD_URL = "https://www.education.ky.gov/AA/Reports/Documents/KY1161534_KY_SP25_Yearbook.pdf"
KY_OUTPUT_RELATIVE_PATH = Path("datasets/ky/ksa/2023_2024/processed/ksa_2024_statewide_grade3_reading_tiers.csv")

LA_SOURCE_PAGE_URL = "https://doe.louisiana.gov/resources/library/test-results"
LA_SOURCE_DOWNLOAD_URL = (
    "https://doe.louisiana.gov/docs/default-source/data-management/"
    "spring-2025-leap-2025-state-lea-achievement-level-summary.xlsx?sfvrsn=bdc2fd31_7"
)
LA_RAW_RELATIVE_PATH = Path("datasets/la/leap/2024_2025/raw/2025_state_lea_achievement_level_summary.xlsx")
LA_OUTPUT_RELATIVE_PATH = Path("datasets/la/leap/2024_2025/processed/leap_2025_statewide_grade3_ela_tiers.csv")

MA_SOURCE_PAGE_URL = "https://profiles.doe.mass.edu/mcas/achievement_level.aspx?linkid=32&orgcode=00000000&orgtypecode=0&"
MA_SOURCE_DOWNLOAD_URL = MA_SOURCE_PAGE_URL
MA_RAW_RELATIVE_PATH = Path("datasets/ma/mcas/2024_2025/raw/achievement_level_2025_state_profile.html")
MA_OUTPUT_RELATIVE_PATH = Path("datasets/ma/mcas/2024_2025/processed/mcas_2025_statewide_grade3_ela_tiers.csv")

MD_SOURCE_PAGE_URL = "https://reportcard.msde.maryland.gov/Graphs/#/Assessments/ELAPerformance"
MD_SOURCE_DOWNLOAD_URL = "https://reportcard.msde.maryland.gov/Assessments/GetELAPerformanceBarChart"
MD_RAW_RELATIVE_PATH = Path("datasets/md/mcap/2024_2025/raw/elaperformance_2025_state_grade3_all_students.json")
MD_OUTPUT_RELATIVE_PATH = Path("datasets/md/mcap/2024_2025/processed/mcap_2025_statewide_grade3_ela_tiers.csv")

MS_SOURCE_PAGE_URL = "https://mdek12.org/wp-content/uploads/sites/33/2025/08/MAAP-2025-Results-Executive-Summary.pdf"
MS_SOURCE_DOWNLOAD_URL = "https://mdek12.org/wp-content/uploads/sites/33/2025/08/MAAP-2025-Results-Executive-Summary.pdf"
MS_OUTPUT_RELATIVE_PATH = Path("datasets/ms/maap/2024_2025/processed/maap_2025_statewide_grade3_ela_tiers.csv")

NC_SOURCE_PAGE_URL = (
    "https://www.dpi.nc.gov/districts-schools/accountability-and-testing/"
    "school-accountability-and-reporting/accountability-data-sets-and-reports"
)
NC_SOURCE_DOWNLOAD_URL = "https://www.dpi.nc.gov/2024-25-school-assessment-and-other-indicator-data-0/download?attachment"
NC_RAW_RELATIVE_PATH = Path("datasets/nc/eog/2024_2025/raw/2024_25_school_assessment_and_other_indicator_data.xlsx")
NC_OUTPUT_RELATIVE_PATH = Path("datasets/nc/eog/2024_2025/processed/eog_2025_statewide_grade3_reading_public_bins.csv")

NH_SOURCE_PAGE_URL = (
    "https://my.doe.nh.gov/iPlatform/Report/DataReportsSubCategory"
    "?reportSubCategoryId=20"
)
NH_SOURCE_DOWNLOAD_URL = NH_SOURCE_PAGE_URL
NH_OUTPUT_RELATIVE_PATH = Path(
    "datasets/nh/nh_sas/2024_2025/processed/nh_sas_2025_statewide_grade3_ela_public_reference.csv"
)

OH_SOURCE_PAGE_URL = "https://reportcard.education.ohio.gov/download"
OH_SOURCE_INDEX_URL = "https://edu-prd-reportcard-datarefresh-api.azurewebsites.net/api/v2/CategoriesFileTypes/2025/0/0"
OH_SOURCE_FILE_TITLE = "Title 1 Proficiency by Grade 2024-2025"
OH_RAW_RELATIVE_PATH = Path("datasets/oh/ost/2024_2025/raw/2025_title_1_proficiency_by_grade.xlsx")
OH_OUTPUT_RELATIVE_PATH = Path("datasets/oh/ost/2024_2025/processed/ost_2025_statewide_grade3_ela_public_reference.csv")

PA_SOURCE_PAGE_URL = "https://www.pa.gov/agencies/education/data-and-reporting/assessment-reporting"
PA_SOURCE_DOWNLOAD_URL = PA_SOURCE_PAGE_URL
PA_RAW_RELATIVE_PATH = Path("datasets/pa/pssa/2024_2025/raw/assessment_reporting_2025.html")
PA_OUTPUT_RELATIVE_PATH = Path("datasets/pa/pssa/2024_2025/processed/pssa_2025_statewide_grade3_ela_tiers.csv")

RI_SOURCE_PAGE_URL = "https://www3.ride.ri.gov/ADP"
RI_SOURCE_DOWNLOAD_URL = (
    "https://www3.ride.ri.gov/ADP/Default/_Data?assessment=5&lea=00&sch=&grade=03"
    "&supergroup=0&schYear=2024-25&compareWith=&ADA=false&Growth=false&Performance=false"
)
RI_RAW_RELATIVE_PATH = Path("datasets/ri/ricas/2024_2025/raw/adp_2025_state_grade3_ela_all_students.json")
RI_OUTPUT_RELATIVE_PATH = Path("datasets/ri/ricas/2024_2025/processed/ricas_2025_statewide_grade3_ela_tiers.csv")

VA_SOURCE_PAGE_URL = "https://schoolquality.virginia.gov/virginia-state-quality-profile"
VA_SOURCE_DOWNLOAD_URL = VA_SOURCE_PAGE_URL
VA_RAW_RELATIVE_PATH = Path("datasets/va/sol/2024_2025/raw/virginia_state_quality_profile.html")
VA_OUTPUT_RELATIVE_PATH = Path("datasets/va/sol/2024_2025/processed/sol_2025_statewide_grade3_reading_public_bins.csv")

NJ_SOURCE_PAGE_URL = "https://www.nj.gov/education/assessment/results/reports/2425/index.shtml"
NJ_SOURCE_DOWNLOAD_URL = "https://www.nj.gov/education/assessment/results/reports/2425/spring/ELA03%20NJSLA%20DATA%202024-25.xlsx"
NJ_RAW_RELATIVE_PATH = Path("datasets/nj/njsla/2024_2025/raw/ela03_njsla_data_2024_25.xlsx")
NJ_OUTPUT_RELATIVE_PATH = Path("datasets/nj/njsla/2024_2025/processed/njsla_2025_statewide_grade3_ela_tiers.csv")

NY_SOURCE_PAGE_URL = "https://data.nysed.gov/downloads.php"
NY_SOURCE_DOWNLOAD_URL = "https://data.nysed.gov/files/essa/24-25/SRC2025.zip"
NY_OUTPUT_RELATIVE_PATH = Path("datasets/ny/nysed_report_card/2024_2025/processed/nysed_2025_statewide_grade3_ela_tiers.csv")

SC_SOURCE_PAGE_URL = (
    "https://ed.sc.gov/data/test-scores/state-assessments/sc-ready/2025/"
    "state-scores-by-grade-level-and-demographic/?districtCode=9999&schoolCode=1001"
)
SC_SOURCE_DOWNLOAD_URL = SC_SOURCE_PAGE_URL
SC_OUTPUT_RELATIVE_PATH = Path("datasets/sc/sc_ready/2024_2025/processed/sc_ready_2025_statewide_grade3_ela_tiers.csv")

TN_SOURCE_PAGE_URL = "https://www.tn.gov/content/tn/education/districts/federal-programs-and-oversight/data/data-downloads.html"
TN_SOURCE_DOWNLOAD_URL = "https://www.tn.gov/content/dam/tn/education/accountability/2025/state_assessment_file_suppressed_2025.xlsx"
TN_RAW_RELATIVE_PATH = Path("datasets/tn/tcap/2024_2025/raw/2025_state_assessment_file_suppressed.xlsx")
TN_OUTPUT_RELATIVE_PATH = Path("datasets/tn/tcap/2024_2025/processed/tcap_2025_statewide_grade3_ela_tiers.csv")

TX_SOURCE_PAGE_URL = "https://rptsvr1.tea.texas.gov/perfreport/tapr/2024/Basic%20Download/DownloadSelData.html"
TX_SOURCE_DOWNLOAD_URL = (
    "https://rptsvr1.tea.texas.gov/cgi/sas/broker"
    "?_service=marykay"
    "&year4=2024"
    "&year2="
    "&prgopt=2024/tapr/Basic%20Download/xplore/getdata2.sas"
    "&_program=perfrept.perfmast.sas"
    "&_debug=0"
    "&step=1"
    "&steps=2"
    "&sumlev=S"
    "&dsname=SSTAAR_GR3"
)
TX_RAW_RELATIVE_PATH = Path("datasets/tx/staar/2023_2024/raw/2023_24_tapr_state_staar_grade3.xlsx")
TX_OUTPUT_RELATIVE_PATH = Path("datasets/tx/staar/2023_2024/processed/staar_2024_statewide_grade3_rla_tiers.csv")
TX_FIELD_GUIDE_RELATIVE_PATH = Path("datasets/tx/staar/2023_2024/metadata/staar_grade3_field_guide.csv")

WA_SOURCE_PAGE_URL = "https://data.wa.gov/api/views/h5d9-vgwi"
WA_SOURCE_DOWNLOAD_URL = "https://data.wa.gov/api/views/h5d9-vgwi/rows.csv?accessType=DOWNLOAD"
WA_RAW_RELATIVE_PATH = Path("datasets/wa/sbac/2024_2025/raw/report_card_assessment_data_2024_25_state_extract.csv")
WA_OUTPUT_RELATIVE_PATH = Path("datasets/wa/sbac/2024_2025/processed/sbac_2025_statewide_grade3_ela_tiers.csv")

WV_SOURCE_PAGE_URL = "https://wvde.us/events/2024/8/august-2024-board-meeting"
WV_SOURCE_DOWNLOAD_URL = "https://wvde.us/sites/default/files/2024-09/2024-Accountability-Assessment-Results-Document.pdf"
WV_TIER_DEFINITIONS_PAGE_URL = (
    "https://wvde.us/academics/assessment/scaled-scored-information/"
    "scale-score-west-virginia-general-summative-assessment"
)
WV_REFERENCE_OUTPUT_RELATIVE_PATH = Path(
    "datasets/wv/wvgsa/2023_2024/processed/wvgsa_2024_statewide_grade3_ela_public_reference.csv"
)

WI_SOURCE_PAGE_URL = "https://dpi.wi.gov/wise-downloads/forwardcertified2024-25"
WI_SOURCE_DOWNLOAD_URL = "https://dpi.wi.gov/sites/default/files/wise/downloads/forward_certified_2024-25.zip"
WI_RAW_RELATIVE_PATH = Path("datasets/wi/forward/2024_2025/raw/forward_certified_2024_25.zip")
WI_OUTPUT_RELATIVE_PATH = Path("datasets/wi/forward/2024_2025/processed/forward_2025_statewide_grade3_ela_tiers.csv")

SUMMARY_RELATIVE_PATH = Path("datasets/summary/statewide_grade3_ela_tiers.csv")
BELOW_BASIC_RELATIVE_PATH = Path("datasets/summary/statewide_grade3_ela_below_basic_analog.csv")
PUBLISHED_REFERENCE_RELATIVE_PATH = Path("datasets/summary/statewide_grade3_ela_published_reference_bins.csv")
ROLLOUT_TRACKER_RELATIVE_PATH = Path("datasets/summary/statewide_grade3_ela_rollout_tracker.csv")
METADATA_RELATIVE_PATH = Path("datasets/summary/metadata/statewide_grade3_ela_sources.json")
CATALOG_RELATIVE_PATH = Path("datasets/catalog.csv")
ED_DATA_EXPRESS_PROXY_RELATIVE_PATH = Path(
    "datasets/us/ed_data_express/multi_year/processed/ed_data_express_statewide_grade3_ela_proficiency_proxy.csv"
)
ED_DATA_EXPRESS_SOURCE_PAGE_URL = "https://eddataexpress.ed.gov/download/data-builder/data-download-tool"

STATE_INFO = [
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "District of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
]

EXACT_TIER_STATES = {
    "AK",
    "AL",
    "AR",
    "AZ",
    "CO",
    "CT",
    "DC",
    "FL",
    "GA",
    "ID",
    "IN",
    "KS",
    "KY",
    "LA",
    "MA",
    "MD",
    "ME",
    "MS",
    "MO",
    "MT",
    "NJ",
    "NY",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "WA",
    "WI",
}
OFFICIAL_PROFICIENCY_ONLY_STATES = {"CA", "DE", "HI", "IA", "IL", "NH", "NM", "OH", "WV", "WY"}
SOURCE_BIN_STATES = {"MI", "NC", "VA"}


OFFICIAL_STATE_RECORDS: dict[str, dict[str, object]] = {
    "AL": {
        "state_name": "Alabama",
        "assessment": "ACAP",
        "program": "ACAP",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "exact_tiers",
        "bins": [
            ("level_1", "Level 1", 9.0),
            ("level_2", "Level 2", 25.0),
            ("level_3", "Level 3", 42.0),
            ("level_4", "Level 4", 23.0),
        ],
        "below_basic_label": "Level 1",
        "proficient_pct": 66.0,
        "valid_test_takers": 55930,
        "output_path": Path(
            "datasets/al/acap/2024_2025/processed/acap_2025_statewide_grade3_ela_tiers.csv"
        ),
        "source_url": (
            "https://www.alabamaachieves.org/wp-content/uploads/2025/07/"
            "SBOE_20250716_2024-2025-Student-Assessment-State-Data-Overview_v1.0.pdf"
        ),
        "source_page_url": "https://www.alabamaachieves.org/assessment/acap/",
        "notes": (
            "Alabama's official 2024-25 state assessment overview reports statewide Grade 3 ACAP ELA "
            "percentages for Levels 1 through 4. Published percentages sum to 99% because of rounding."
        ),
    },
    "AZ": {
        "state_name": "Arizona",
        "assessment": "AASA",
        "program": "AASA",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "exact_tiers",
        "bins": [
            ("minimally_proficient", "Minimally Proficient", 51.7),
            ("partially_proficient", "Partially Proficient", 12.5),
            ("proficient", "Proficient", 22.8),
            ("highly_proficient", "Highly Proficient", 13.1),
        ],
        "below_basic_label": "Minimally Proficient",
        "proficient_pct": 35.9,
        "valid_test_takers": 79299,
        "output_path": Path(
            "datasets/az/aasa/2024_2025/processed/aasa_2025_statewide_grade3_ela_tiers.csv"
        ),
        "source_url": "https://www.azed.gov/sites/default/files/2026/04/AASA_2025_Technical_Report.pdf",
        "source_page_url": "https://www.azed.gov/assessment/assessments/aasa",
        "notes": (
            "Arizona's official AASA 2025 technical report, Table C.1, reports statewide Grade 3 ELA "
            "counts and percentages for all four performance levels."
        ),
    },
    "HI": {
        "state_name": "Hawaii",
        "assessment": "Smarter Balanced",
        "program": "SMARTER_BALANCED",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "proficiency_only",
        "proficient_label": "Met or Exceeded Achievement Standard",
        "proficient_pct": 49.9,
        "valid_test_takers": 12122,
        "below_basic_label": "100 - Met or Exceeded Achievement Standard",
        "output_path": Path(
            "datasets/hi/smarter_balanced/2024_2025/processed/"
            "sba_2025_statewide_grade3_ela_public_reference.csv"
        ),
        "source_url": "https://hawaiipublicschools.org/wp-content/uploads/SBA2024-25.xlsx",
        "source_page_url": "https://hawaiipublicschools.org/academics/types-of-testing/",
        "notes": (
            "Hawaii's official 2024-25 Smarter Balanced statewide workbook reports 49.9% of Grade 3 "
            "ELA students met or exceeded the achievement standard, but the state row used here does "
            "not publish the full performance-level split."
        ),
    },
    "ID": {
        "state_name": "Idaho",
        "assessment": "ISAT",
        "program": "ISAT",
        "school_year": "2023-2024",
        "administration_year": 2024,
        "record_kind": "exact_tiers",
        "bins": [
            ("level_1", "Level 1", 29.0),
            ("level_2", "Level 2", 23.0),
            ("level_3", "Level 3", 22.0),
            ("level_4", "Level 4", 25.0),
        ],
        "below_basic_label": "Level 1",
        "proficient_pct": 48.0,
        "valid_test_takers": 23374,
        "output_path": Path(
            "datasets/id/isat/2023_2024/processed/isat_2024_statewide_grade3_ela_tiers.csv"
        ),
        "source_url": (
            "https://www.sde.idaho.gov/assessment/isat-cas/files/general/"
            "SY2023-24-Idaho-SB-Tech-Report.pdf"
        ),
        "source_page_url": (
            "https://www.sde.idaho.gov/about-us/departments/assessment-accountability/"
            "idaho-standards-achievement-test-isat/"
        ),
        "notes": (
            "Idaho's official 2023-24 ISAT technical report publishes statewide Grade 3 ELA "
            "percentages for Levels 1 through 4. This one-year-older state result replaces the older "
            "federal proficiency proxy; published level percentages sum to 99% because of rounding."
        ),
    },
    "IL": {
        "state_name": "Illinois",
        "assessment": "IAR",
        "program": "IAR",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "proficiency_only",
        "proficient_label": "Proficient",
        "proficient_pct": 47.3,
        "below_basic_label": "100 - Proficient",
        "output_path": Path(
            "datasets/il/iar/2024_2025/processed/iar_2025_statewide_grade3_ela_public_reference.csv"
        ),
        "source_url": "https://www.isbe.net/Documents/2025-Report-Card-Public-Data-Set.xlsx",
        "source_page_url": "https://www.isbe.net/Pages/Illinois-State-Report-Card-Data.aspx",
        "notes": (
            "Illinois's official 2025 Report Card public dataset reports statewide Grade 3 IAR ELA "
            "proficiency at 47.3%. The statewide row used here does not expose the full performance-level split."
        ),
    },
    "IA": {
        "state_name": "Iowa",
        "assessment": "ISASP",
        "program": "ISASP",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "proficiency_only",
        "proficient_label": "Proficient",
        "proficient_pct": 68.0,
        "below_basic_label": "100 - Proficient",
        "output_path": Path(
            "datasets/ia/isasp/2024_2025/processed/isasp_2025_statewide_grade3_ela_public_reference.csv"
        ),
        "source_url": "https://educate.iowa.gov/media/11696/download?inline=",
        "source_page_url": (
            "https://educate.iowa.gov/press-release/2025-08-20/"
            "iowa-achieves-impressive-gains-early-literacy-science-new-2025-spring-statewide-student-assessment"
        ),
        "notes": (
            "Iowa's official 2025 statewide assessment results report Grade 3 ELA proficiency at 68%. "
            "The public statewide summary used here does not expose the full performance-level split."
        ),
    },
    "KS": {
        "state_name": "Kansas",
        "assessment": "Kansas State Assessment",
        "program": "KSA",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "exact_tiers",
        "bins": [
            ("level_1", "Level 1", 27.2),
            ("level_2", "Level 2", 20.9),
            ("level_3", "Level 3", 39.2),
            ("level_4", "Level 4", 12.7),
        ],
        "below_basic_label": "Level 1",
        "proficient_pct": 51.9,
        "output_path": Path(
            "datasets/ks/ksa/2024_2025/processed/ksa_2025_statewide_grade3_ela_tiers.csv"
        ),
        "source_url": (
            "https://www.ksde.gov/docs/default-source/crp/ar-2024-25-coherence.pdf"
            "?sfvrsn=42d42afb_3"
        ),
        "source_page_url": "https://www.ksde.gov/Home/Quick-Links/News-Room/Annual-Reports",
        "notes": (
            "Kansas's official 2024-25 annual report publishes statewide Grade 3 ELA percentages "
            "for Kansas State Assessment Levels 1 through 4."
        ),
    },
    "ME": {
        "state_name": "Maine",
        "assessment": "Maine Through Year Assessment",
        "program": "MTYA",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "exact_tiers",
        "bins": [
            ("well_below_state_expectations", "Well Below State Expectations", 12.6),
            ("below_state_expectations", "Below State Expectations", 27.1),
            ("at_state_expectations", "At State Expectations", 47.3),
            ("above_state_expectations", "Above State Expectations", 13.0),
        ],
        "below_basic_label": "Well Below State Expectations",
        "proficient_pct": 60.3,
        "valid_test_takers": 12530,
        "output_path": Path(
            "datasets/me/mtya/2024_2025/processed/mtya_2025_statewide_grade3_reading_tiers.csv"
        ),
        "source_url": (
            "https://www.maine.gov/doe/sites/maine.gov.doe/files/inline-files/"
            "Assessment%20-%20Maine%20Through%20Year%20Assessment%20Spring%2025%20Technical%20Report%20-%203.31.2026.pdf"
        ),
        "source_page_url": (
            "https://www.maine.gov/doe/Testing_Accountability/MECAS/math_ELA_Literacy"
        ),
        "notes": (
            "Maine's official Spring 2025 technical report, Table 8.2, publishes statewide Grade 3 "
            "Reading percentages for all four achievement levels."
        ),
    },
    "MI": {
        "state_name": "Michigan",
        "assessment": "M-STEP",
        "program": "MSTEP",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "source_bins",
        "bins": [
            ("not_proficient", "Not Proficient", 36.5),
            ("partially_proficient", "Partially Proficient", 24.6),
            ("proficient_or_advanced", "Proficient or Advanced", 38.9),
        ],
        "below_basic_label": "Not Proficient",
        "proficient_pct": 38.9,
        "output_path": Path(
            "datasets/mi/mstep/2024_2025/processed/mstep_2025_statewide_grade3_ela_public_bins.csv"
        ),
        "source_url": (
            "https://www.michigan.gov/mde/news-and-information/press-releases/2025/08/27/"
            "michigan-students-perform-better-on-most-tests"
        ),
        "source_page_url": (
            "https://www.michigan.gov/mde/news-and-information/press-releases/2025/08/27/"
            "michigan-students-perform-better-on-most-tests"
        ),
        "notes": (
            "Michigan's official 2025 release reports 38.9% Proficient or Advanced and 24.6% "
            "Partially Proficient for Grade 3 M-STEP ELA. Not Proficient is the remaining 36.5%; "
            "the state release combines the two upper tiers."
        ),
    },
    "MO": {
        "state_name": "Missouri",
        "assessment": "MAP",
        "program": "MAP",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "exact_tiers",
        "bins": [
            ("below_basic", "Below Basic", 18.0),
            ("basic", "Basic", 23.0),
            ("proficient", "Proficient", 28.0),
            ("advanced", "Advanced", 31.0),
        ],
        "below_basic_label": "Below Basic",
        "proficient_pct": 59.0,
        "valid_test_takers": 65733,
        "output_path": Path(
            "datasets/mo/map/2024_2025/processed/map_2025_statewide_grade3_ela_tiers.csv"
        ),
        "source_url": (
            "https://dese.mo.gov/sites/g/files/zuston521/files/media/pdf/2025/08/"
            "2024-25%20Preliminary%20MAP%20Results%2008.22.2025.pdf"
        ),
        "source_page_url": (
            "https://dese.mo.gov/media/pdf/report-2024-25-preliminary-academic-performance"
        ),
        "notes": (
            "Missouri's official preliminary 2024-25 MAP results publish statewide Grade 3 ELA "
            "percentages for Below Basic, Basic, Proficient, and Advanced."
        ),
    },
    "MT": {
        "state_name": "Montana",
        "assessment": "MAST",
        "program": "MAST",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "exact_tiers",
        "bins": [
            ("novice", "Novice", 32.8),
            ("partially_proficient", "Partially Proficient", 31.3),
            ("proficient", "Proficient", 28.8),
            ("advanced", "Advanced", 7.2),
        ],
        "below_basic_label": "Novice",
        "proficient_pct": 36.0,
        "valid_test_takers": 11239,
        "output_path": Path(
            "datasets/mt/mast/2024_2025/processed/mast_2025_statewide_grade3_ela_tiers.csv"
        ),
        "source_url": (
            "https://opi.mt.gov/Portals/182/Page%20Files/Statewide%20Testing/MAST/"
            "MAST%202024-2025%20Technical%20Report.pdf?ver=2025-12-19-121316-830"
        ),
        "source_page_url": (
            "https://opi.mt.gov/Leadership/Assessment-Accountability/MontCAS/Assessment-Data-Release"
        ),
        "notes": (
            "Montana's official 2024-25 MAST technical report publishes statewide Grade 3 ELA "
            "counts and percentages for Novice through Advanced. Published percentages sum to "
            "100.1% because of rounding."
        ),
    },
    "NM": {
        "state_name": "New Mexico",
        "assessment": "NM-MSSA",
        "program": "NM_MSSA",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "proficiency_only",
        "proficient_label": "Proficient",
        "proficient_pct": 41.0,
        "below_basic_label": "100 - Proficient",
        "output_path": Path(
            "datasets/nm/nm_mssa/2024_2025/processed/"
            "nm_mssa_2025_statewide_grade3_ela_public_reference.csv"
        ),
        "source_url": (
            "https://web.ped.nm.gov/wp-content/uploads/2025/10/"
            "PED-Assessment-Presentation-for-LESC_101525.pdf"
        ),
        "source_page_url": (
            "https://web.ped.nm.gov/bureaus/accountability/achievement-data-by-year/"
        ),
        "notes": (
            "New Mexico PED's official 2025 assessment presentation reports Grade 3 literacy "
            "proficiency at 41%. The Grade 3 public result used here does not expose the full "
            "NM-MSSA performance-level split."
        ),
    },
    "OK": {
        "state_name": "Oklahoma",
        "assessment": "OSTP",
        "program": "OSTP",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "exact_tiers",
        "bins": [
            ("below_basic", "Below Basic", 43.0),
            ("basic", "Basic", 30.0),
            ("proficient", "Proficient", 24.0),
            ("advanced", "Advanced", 3.0),
        ],
        "below_basic_label": "Below Basic",
        "proficient_pct": 27.0,
        "valid_test_takers": 49994,
        "output_path": Path(
            "datasets/ok/ostp/2024_2025/processed/ostp_2025_statewide_grade3_ela_tiers.csv"
        ),
        "source_url": (
            "https://oklahoma.gov/content/dam/ok/en/osde/documents/services/assessments/"
            "state-testing-resources/2025-state-testing-resources/2425OKOSTPMediaRedacted.csv"
        ),
        "source_page_url": (
            "https://oklahoma.gov/education/services/assessments/state-testing-resources.html"
        ),
        "notes": (
            "Oklahoma's official 2024-25 OSTP public CSV reports statewide Grade 3 ELA counts "
            "and percentages for Below Basic through Advanced."
        ),
    },
    "OR": {
        "state_name": "Oregon",
        "assessment": "OSAS",
        "program": "OSAS",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "exact_tiers",
        "bins": [
            ("level_1", "Level 1", 35.9),
            ("level_2", "Level 2", 23.9),
            ("level_3", "Level 3", 19.6),
            ("level_4", "Level 4", 20.7),
        ],
        "below_basic_label": "Level 1",
        "proficient_pct": 40.3,
        "valid_test_takers": 38826,
        "output_path": Path(
            "datasets/or/osas/2024_2025/processed/osas_2025_statewide_grade3_ela_tiers.csv"
        ),
        "source_url": (
            "https://www.oregon.gov/ode/educator-resources/assessment/Documents/"
            "TestResults2425/pagr_State_ELA_2425.xlsx"
        ),
        "source_page_url": (
            "https://www.oregon.gov/ode/educator-resources/assessment/pages/"
            "assessment-group-reports.aspx"
        ),
        "notes": (
            "Oregon's official 2024-25 statewide ELA workbook reports Grade 3 OSAS counts and "
            "percentages for Levels 1 through 4. Published percentages sum to 100.1% because of rounding."
        ),
    },
    "SD": {
        "state_name": "South Dakota",
        "assessment": "South Dakota Assessment",
        "program": "SDA",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "record_kind": "exact_tiers",
        "bins": [
            ("level_1", "Level 1", 30.0),
            ("level_2", "Level 2", 26.0),
            ("level_3", "Level 3", 23.0),
            ("level_4", "Level 4", 22.0),
        ],
        "below_basic_label": "Level 1",
        "proficient_pct": 45.0,
        "valid_test_takers": 10929,
        "output_path": Path(
            "datasets/sd/sd_assessments/2024_2025/processed/"
            "sd_2025_statewide_grade3_ela_tiers.csv"
        ),
        "source_url": "https://doe.sd.gov/Assessment/documents/SY25-SBTech.pdf",
        "source_page_url": "https://doe.sd.gov/Assessment/SD-assessments.aspx",
        "notes": (
            "South Dakota's official 2024-25 ELA and mathematics technical report, Table 23, "
            "publishes statewide Grade 3 ELA percentages for Levels 1 through 4. Published "
            "percentages sum to 101% because of rounding."
        ),
    },
    "WY": {
        "state_name": "Wyoming",
        "assessment": "WY-TOPP",
        "program": "WY_TOPP",
        "school_year": "2023-2024",
        "administration_year": 2024,
        "record_kind": "proficiency_only",
        "proficient_label": "Proficient",
        "proficient_pct": 48.0,
        "below_basic_label": "100 - Proficient",
        "output_path": Path(
            "datasets/wy/wy_topp/2023_2024/processed/"
            "wy_topp_2024_statewide_grade3_ela_public_reference.csv"
        ),
        "source_url": (
            "https://edu.wyoming.gov/wp-content/uploads/2024/02/"
            "How-to-Use-Statewide-Summative-Assessment-Data-Public.pdf"
        ),
        "source_page_url": "https://edu.wyoming.gov/data/assessment-reports/",
        "notes": (
            "Wyoming's official statewide assessment guidance reports Grade 3 ELA proficiency "
            "at 48%. This 2023-24 state result replaces the older federal proxy; the public "
            "reference used here does not expose the full WY-TOPP performance-level split."
        ),
    },
}


def _copy_or_download_file(
    repo_root: Path,
    session: requests.Session,
    destination_relative_path: Path,
    source_url: str,
    local_override: Path | None,
    request_headers: dict[str, str] | None = None,
) -> Path:
    destination = repo_root / destination_relative_path
    ensure_parent(destination)

    if local_override is not None:
        source = local_override.resolve()
        if source != destination.resolve():
            shutil.copyfile(source, destination)
        return destination

    if destination.exists():
        return destination

    response = session.get(source_url, headers=request_headers, timeout=120)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination


def _write_single_row_csv(repo_root: Path, output_relative_path: Path, row: dict[str, object]) -> Path:
    output_path = repo_root / output_relative_path
    ensure_parent(output_path)
    pd.DataFrame([row]).to_csv(output_path, index=False)
    return output_path


def _build_official_state_records(
    repo_root: Path,
) -> tuple[
    pd.DataFrame,
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, Path],
    list[dict[str, str]],
]:
    tier_frames: list[pd.DataFrame] = []
    below_basic_rows: list[dict[str, object]] = []
    published_reference_rows: list[dict[str, object]] = []
    output_paths: dict[str, Path] = {}
    catalog_entries: list[dict[str, str]] = []

    for state_code, record in OFFICIAL_STATE_RECORDS.items():
        state_name = str(record["state_name"])
        assessment = str(record["assessment"])
        school_year = str(record["school_year"])
        administration_year = int(record["administration_year"])
        record_kind = str(record["record_kind"])
        below_basic_label = str(record["below_basic_label"])
        source_url = str(record["source_url"])
        source_page_url = str(record["source_page_url"])
        notes = str(record["notes"])
        output_relative_path = Path(record["output_path"])
        output_path = repo_root / output_relative_path
        ensure_parent(output_path)

        bins = list(record.get("bins", []))
        if record_kind == "proficiency_only":
            proficient_pct = float(record["proficient_pct"])
            below_basic_pct = round(100.0 - proficient_pct, 1)
        else:
            matching_bins = [float(value) for _, label, value in bins if label == below_basic_label]
            if len(matching_bins) != 1:
                raise RuntimeError(
                    f"{state_code} official state record must contain exactly one below-basic bin."
                )
            below_basic_pct = matching_bins[0]

        summary: dict[str, object] = {
            "state": state_code,
            "state_name": state_name,
            "assessment": assessment,
            "subject": "ELA",
            "grade": "03",
            "school_year": school_year,
            "administration_year": administration_year,
            "below_basic_analog_label": below_basic_label,
            "below_basic_analog_pct": below_basic_pct,
            "source_notes": notes,
            "source_url": source_url,
            "source_page_url": source_page_url,
        }
        if "proficient_pct" in record:
            summary["official_statewide_grade3_ela_percent_proficient_pct"] = float(
                record["proficient_pct"]
            )
        if "valid_test_takers" in record:
            summary["official_valid_test_takers"] = int(record["valid_test_takers"])
        below_basic_rows.append(summary)

        published_reference: dict[str, object] = {
            "state": state_code,
            "state_name": state_name,
            "assessment": assessment,
            "subject": "ELA",
            "grade": "03",
            "school_year": school_year,
            "administration_year": administration_year,
            "source_bin_structure": (
                "published_exact_tiers"
                if record_kind == "exact_tiers"
                else "published_source_bins"
                if record_kind == "source_bins"
                else "published_proficiency_only"
            ),
            "notes": notes,
            "source_url": source_url,
            "source_page_url": source_page_url,
        }
        if record_kind == "proficiency_only":
            reference_bins = [
                (
                    str(record.get("proficient_label", "Proficient")),
                    float(record["proficient_pct"]),
                )
            ]
        else:
            reference_bins = [(str(label), float(value)) for _, label, value in bins]
        for index in range(1, 6):
            if index <= len(reference_bins):
                label, value = reference_bins[index - 1]
                published_reference[f"source_bin_{index}_label"] = label
                published_reference[f"source_bin_{index}_pct"] = value
            else:
                published_reference[f"source_bin_{index}_label"] = ""
                published_reference[f"source_bin_{index}_pct"] = None
        published_reference_rows.append(published_reference)

        if record_kind == "exact_tiers":
            tier_rows: list[dict[str, object]] = []
            for tier_rank, (tier_id, tier_label, value) in enumerate(bins, start=1):
                tier_rows.append(
                    {
                        "state": state_code,
                        "state_name": state_name,
                        "assessment": assessment,
                        "subject": "ELA",
                        "subject_label": "English Language Arts",
                        "grade": "03",
                        "school_year": school_year,
                        "administration_year": administration_year,
                        "tier_rank": tier_rank,
                        "tier_id": str(tier_id),
                        "tier_label": str(tier_label),
                        "pct_students": float(value),
                        "is_below_basic_analog": str(tier_label) == below_basic_label,
                        "below_basic_analog_label": below_basic_label,
                        "source_value_kind": "reported_exact_tier",
                        "notes": notes,
                        "source_url": source_url,
                        "source_page_url": source_page_url,
                    }
                )
            processed_df = pd.DataFrame(tier_rows)
            tier_frames.append(processed_df)
        else:
            processed_df = pd.DataFrame([published_reference])
        processed_df.to_csv(output_path, index=False)

        output_key = (
            f"{state_code.lower()}_statewide_tiers"
            if record_kind == "exact_tiers"
            else f"{state_code.lower()}_public_reference"
        )
        output_paths[output_key] = output_path
        catalog_entries.append(
            {
                "state": state_code,
                "state_name": state_name,
                "program": str(record["program"]),
                "reporting_period": school_year,
                "kind": "processed",
                "granularity": "state",
                "description": (
                    f"Statewide Grade 3 ELA {assessment} "
                    + (
                        "exact performance tiers."
                        if record_kind == "exact_tiers"
                        else "published source bins."
                        if record_kind == "source_bins"
                        else "official proficiency-only public reference."
                    )
                ),
                "path": str(output_relative_path),
                "source_url": source_url,
            }
        )

    all_tiers = pd.concat(tier_frames, ignore_index=True) if tier_frames else pd.DataFrame()
    return all_tiers, below_basic_rows, published_reference_rows, output_paths, catalog_entries


def _strip_html_text(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", value)).replace("\xa0", " ").strip()


def _build_ed_data_express_proxy_rows(
    repo_root: Path,
) -> tuple[pd.DataFrame, list[dict[str, object]], list[dict[str, object]]]:
    source_path = repo_root / ED_DATA_EXPRESS_PROXY_RELATIVE_PATH
    if not source_path.exists():
        return pd.DataFrame(), [], []

    proxy_df = pd.read_csv(source_path, dtype={"state": str, "grade": str, "school_year": str})
    proxy_df["grade"] = proxy_df["grade"].astype(str).str.zfill(2)

    below_basic_rows: list[dict[str, object]] = []
    published_reference_rows: list[dict[str, object]] = []
    for row in proxy_df.to_dict("records"):
        below_basic_rows.append(
            {
                "state": row["state"],
                "state_name": row["state_name"],
                "assessment": row["assessment"],
                "subject": row["subject"],
                "grade": row["grade"],
                "school_year": row["school_year"],
                "administration_year": int(row["administration_year"]),
                "below_basic_analog_label": "100 - Percent Proficient",
                "below_basic_analog_pct": float(row["below_basic_analog_pct"]),
                "official_statewide_grade3_ela_percent_proficient_pct": float(row["percent_proficient"]),
                "official_valid_test_takers": int(row["valid_test_takers"]),
                "source_notes": row["source_notes"],
                "source_url": row["source_url"],
                "source_page_url": row["source_page_url"],
            }
        )
        published_reference_rows.append(
            {
                "state": row["state"],
                "state_name": row["state_name"],
                "assessment": row["assessment"],
                "subject": row["subject"],
                "grade": row["grade"],
                "school_year": row["school_year"],
                "administration_year": int(row["administration_year"]),
                "source_bin_structure": "federal_proficiency_only_proxy",
                "source_bin_1_label": "Percent Proficient",
                "source_bin_1_pct": float(row["percent_proficient"]),
                "notes": row["source_notes"],
                "source_url": row["source_url"],
                "source_page_url": row["source_page_url"],
            }
        )

    return proxy_df, below_basic_rows, published_reference_rows


def _build_alaska_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_pdf: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=AK_RAW_RELATIVE_PATH,
        source_url=AK_SOURCE_DOWNLOAD_URL,
        local_override=raw_pdf,
    )

    source_note = (
        "Alaska publishes exact statewide Grade 3 AK STAR ELA performance-level percentages in the 2025 assessment brief. "
        "The companion statewide results page reports the Grade 3 Advanced/Proficient share, enrollment, and participation rate."
    )
    tier_specs = [
        ("needs_support", "Needs Support", 36.3, True),
        ("approaching_proficient", "Approaching Proficient", 35.0, False),
        ("proficient", "Proficient", 18.8, False),
        ("advanced", "Advanced", 9.9, False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "AK",
                "state_name": "Alaska",
                "assessment": "AK STAR",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Needs Support",
                "source_value_kind": "reported_exact_tier",
                "notes": source_note,
                "source_url": AK_SOURCE_DOWNLOAD_URL,
                "source_page_url": AK_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / AK_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "AK",
        "state_name": "Alaska",
        "assessment": "AK STAR",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Needs Support",
        "below_basic_analog_pct": 36.3,
        "official_statewide_grade3_ela_advanced_or_proficient_pct": 28.68,
        "official_enrollment": 9861,
        "official_statewide_grade3_ela_participation_rate": 83.76,
        "source_notes": (
            source_note
            + " The published exact bins sum to 28.7 percent proficient or advanced, consistent with the results page's 28.68 percent."
        ),
        "source_url": AK_SOURCE_DOWNLOAD_URL,
        "source_page_url": AK_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "AK",
        "state_name": "Alaska",
        "assessment": "AK STAR",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Needs Support",
        "source_bin_1_pct": 36.3,
        "source_bin_2_label": "Approaching Proficient",
        "source_bin_2_pct": 35.0,
        "source_bin_3_label": "Proficient",
        "source_bin_3_pct": 18.8,
        "source_bin_4_label": "Advanced",
        "source_bin_4_pct": 9.9,
        "source_bin_5_label": "Advanced / Proficient",
        "source_bin_5_pct": 28.68,
        "notes": (
            "These are Alaska's published statewide Grade 3 AK STAR ELA source bins, plus the companion results page's "
            "Advanced / Proficient share."
        ),
        "source_url": AK_SOURCE_DOWNLOAD_URL,
        "source_page_url": AK_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_california_public_reference(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=CA_RAW_RELATIVE_PATH,
        source_url=CA_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, sheet_name="English Language Arts - 3", header=None)
    grade3_rows = df[df.iloc[:, 0].fillna("").astype(str).str.strip().eq("3")]
    if grade3_rows.empty:
        grade3_rows = df[df.iloc[:, 0].fillna("").astype(str).str.strip().eq("3.0")]
    if grade3_rows.empty:
        raise RuntimeError("Could not find the California statewide Grade 3 ELA row in the CAASPP workbook.")

    record = grade3_rows.iloc[0]
    with_scores = clean_number(record.iloc[1])
    met_or_exceeded_pct = clean_number(record.iloc[4])
    below_basic_proxy_pct = None
    if met_or_exceeded_pct is not None:
        below_basic_proxy_pct = round(100.0 - met_or_exceeded_pct, 2)

    source_note = (
        "California's 2025 CAASPP ELA statewide Grade 3 workbook publishes WithScores and Standard Met/Exceeded only. "
        "The public workbook used here does not expose the full statewide performance-level split."
    )
    summary = {
        "state": "CA",
        "state_name": "California",
        "assessment": "CAASPP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "100 - Standard Met/Exceeded",
        "below_basic_analog_pct": below_basic_proxy_pct,
        "official_statewide_grade3_ela_standard_met_or_exceeded_pct": met_or_exceeded_pct,
        "official_with_scores": with_scores,
        "source_notes": (
            source_note
            + " The below-basic analog remains a not-met proxy defined here as 100 - Standard Met/Exceeded."
        ),
        "source_url": CA_SOURCE_DOWNLOAD_URL,
        "source_page_url": CA_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "CA",
        "state_name": "California",
        "assessment": "CAASPP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_proficiency_only",
        "source_bin_1_label": "Standard Met/Exceeded",
        "source_bin_1_pct": met_or_exceeded_pct,
        "source_bin_2_label": "",
        "source_bin_2_pct": None,
        "source_bin_3_label": "",
        "source_bin_3_pct": None,
        "source_bin_4_label": "",
        "source_bin_4_pct": None,
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": source_note,
        "source_url": CA_SOURCE_DOWNLOAD_URL,
        "source_page_url": CA_SOURCE_PAGE_URL,
    }
    _write_single_row_csv(repo_root, CA_OUTPUT_RELATIVE_PATH, published_reference)
    return summary, published_reference


def _build_colorado_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=CO_RAW_RELATIVE_PATH,
        source_url=CO_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, header=17, dtype=str).dropna(how="all").copy()
    row = df[
        df["Level"].fillna("").astype(str).str.upper().eq("STATE")
        & df["Content"].fillna("").astype(str).str.strip().str.lower().eq("english language arts")
        & df["Grade"].fillna("").astype(str).str.strip().str.zfill(2).eq("03")
    ]
    if row.empty:
        raise RuntimeError("Could not find the Colorado statewide Grade 3 ELA row in the CMAS workbook.")

    record = row.iloc[0]
    tier_specs = [
        ("did_not_yet_meet_expectations", "Did Not Yet Meet Expectations", record["Percent Did Not Yet Meet Expectations"], True),
        ("partially_met_expectations", "Partially Met Expectations", record["Percent Partially Met Expectations"], False),
        ("approached_expectations", "Approached Expectations", record["Percent Approached Expectations"], False),
        ("met_expectations", "Met Expectations", record["Percent Met Expectations"], False),
        ("exceeded_expectations", "Exceeded Expectations", record["Percent Exceeded Expectations"], False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "CO",
                "state_name": "Colorado",
                "assessment": "CMAS",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": clean_number(value),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Did Not Yet Meet Expectations",
                "source_value_kind": "reported_exact_tier",
                "notes": "Colorado publishes exact CMAS performance-level percentages for statewide Grade 3 ELA.",
                "source_url": CO_SOURCE_DOWNLOAD_URL,
                "source_page_url": CO_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / CO_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "CO",
        "state_name": "Colorado",
        "assessment": "CMAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Did Not Yet Meet Expectations",
        "below_basic_analog_pct": clean_number(record["Percent Did Not Yet Meet Expectations"]),
        "official_statewide_grade3_ela_met_or_exceeded_pct": clean_number(record["2025"]),
        "source_notes": "Exact tier percentages are reported directly in the Colorado CMAS statewide workbook.",
        "source_url": CO_SOURCE_DOWNLOAD_URL,
        "source_page_url": CO_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "CO",
        "state_name": "Colorado",
        "assessment": "CMAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Did Not Yet Meet Expectations",
        "source_bin_1_pct": clean_number(record["Percent Did Not Yet Meet Expectations"]),
        "source_bin_2_label": "Partially Met Expectations",
        "source_bin_2_pct": clean_number(record["Percent Partially Met Expectations"]),
        "source_bin_3_label": "Approached Expectations",
        "source_bin_3_pct": clean_number(record["Percent Approached Expectations"]),
        "source_bin_4_label": "Met Expectations",
        "source_bin_4_pct": clean_number(record["Percent Met Expectations"]),
        "source_bin_5_label": "Exceeded Expectations",
        "source_bin_5_pct": clean_number(record["Percent Exceeded Expectations"]),
        "notes": "Colorado publishes exact statewide CMAS performance tiers directly.",
        "source_url": CO_SOURCE_DOWNLOAD_URL,
        "source_page_url": CO_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_connecticut_tiers(
    repo_root: Path,
    raw_json: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = repo_root / CT_RAW_RELATIVE_PATH
    ensure_parent(raw_path)

    if raw_json is not None:
        source = raw_json.resolve()
        if source != raw_path.resolve():
            shutil.copyfile(source, raw_path)
    elif not raw_path.exists():
        raise RuntimeError(
            "Connecticut raw extract is missing. Save the public EdSight Grade 3 ELA report extract to "
            f"{raw_path} or pass --ct-raw-json."
        )

    with raw_path.open() as infile:
        source_data = json.load(infile)

    level_lookup = {
        str(entry["label"]).strip(): entry for entry in source_data.get("performance_levels", [])
    }
    expected_levels = [
        "Level 1 Not Met",
        "Level 2 Approaching",
        "Level 3 Met",
        "Level 4 Exceeded",
    ]
    missing_levels = [level for level in expected_levels if level not in level_lookup]
    if missing_levels:
        raise RuntimeError(
            "Connecticut saved extract is missing Grade 3 ELA performance levels: "
            + ", ".join(missing_levels)
        )

    met_or_exceeded = source_data.get("met_or_exceeded", {})
    met_or_exceeded_pct = clean_number(met_or_exceeded.get("pct"))
    total_students = clean_number(source_data.get("total_number_of_students"))
    total_tested = clean_number(source_data.get("total_number_tested"))
    participation_rate = clean_number(source_data.get("participation_rate"))
    number_scored = clean_number(source_data.get("total_number_with_scored_tests"))
    average_vss = clean_number(source_data.get("average_vss"))

    source_note = (
        "Connecticut EdSight's public Smarter Balanced report publishes the statewide Grade 3 ELA performance-level "
        "percentages directly for All Students."
    )
    tier_specs = [
        ("level_1_not_met", "Level 1 Not Met", clean_number(level_lookup["Level 1 Not Met"].get("pct")), True),
        ("level_2_approaching", "Level 2 Approaching", clean_number(level_lookup["Level 2 Approaching"].get("pct")), False),
        ("level_3_met", "Level 3 Met", clean_number(level_lookup["Level 3 Met"].get("pct")), False),
        ("level_4_exceeded", "Level 4 Exceeded", clean_number(level_lookup["Level 4 Exceeded"].get("pct")), False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "CT",
                "state_name": "Connecticut",
                "assessment": "Smarter Balanced",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Level 1 Not Met",
                "source_value_kind": "reported_exact_tier",
                "notes": source_note,
                "source_url": CT_SOURCE_DOWNLOAD_URL,
                "source_page_url": CT_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / CT_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "CT",
        "state_name": "Connecticut",
        "assessment": "Smarter Balanced",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Level 1 Not Met",
        "below_basic_analog_pct": clean_number(level_lookup["Level 1 Not Met"].get("pct")),
        "official_statewide_grade3_ela_met_or_exceeded_pct": met_or_exceeded_pct,
        "official_total_students": total_students,
        "official_valid_test_takers": total_tested,
        "official_number_scored": number_scored,
        "official_statewide_grade3_ela_participation_rate": participation_rate,
        "source_notes": (
            source_note
            + f" The saved extract also reports {total_students} total students, {total_tested} tested, "
            f"{number_scored} scored tests, and an average VSS of {average_vss}."
        ),
        "source_url": CT_SOURCE_DOWNLOAD_URL,
        "source_page_url": CT_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "CT",
        "state_name": "Connecticut",
        "assessment": "Smarter Balanced",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Level 1 Not Met",
        "source_bin_1_pct": clean_number(level_lookup["Level 1 Not Met"].get("pct")),
        "source_bin_2_label": "Level 2 Approaching",
        "source_bin_2_pct": clean_number(level_lookup["Level 2 Approaching"].get("pct")),
        "source_bin_3_label": "Level 3 Met",
        "source_bin_3_pct": clean_number(level_lookup["Level 3 Met"].get("pct")),
        "source_bin_4_label": "Level 4 Exceeded",
        "source_bin_4_pct": clean_number(level_lookup["Level 4 Exceeded"].get("pct")),
        "source_bin_5_label": "Level 3&4 Met or Exceeded",
        "source_bin_5_pct": met_or_exceeded_pct,
        "notes": (
            "These are Connecticut's published statewide 2024-25 Grade 3 Smarter Balanced ELA source bins, plus "
            "the combined Level 3&4 Met or Exceeded percentage."
        ),
        "source_url": CT_SOURCE_DOWNLOAD_URL,
        "source_page_url": CT_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_dc_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=DC_RAW_RELATIVE_PATH,
        source_url=DC_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    performance_df = pd.read_excel(raw_path, sheet_name="Performance Level", dtype=str).dropna(how="all").copy()
    performance_rows = performance_df[
        performance_df["Aggregation Level"].fillna("").astype(str).str.strip().eq("State")
        & performance_df["Assessment Name"].fillna("").astype(str).str.strip().eq("DCCAPE")
        & performance_df["Subject"].fillna("").astype(str).str.strip().eq("ELA")
        & performance_df["Student Group"].fillna("").astype(str).str.strip().eq("All Students")
        & performance_df["Student Group Value"].fillna("").astype(str).str.strip().eq("All Students")
        & performance_df["Enrolled Grade or Course"].fillna("").astype(str).str.strip().eq("Grade 3-All")
    ].copy()
    if performance_rows.empty:
        raise RuntimeError(
            "Could not find the District of Columbia statewide Grade 3 DCCAPE ELA rows in the OSSE workbook."
        )

    performance_by_metric = {
        str(row["Metric"]).strip(): row for _, row in performance_rows.iterrows()
    }
    tier_specs = [
        ("level_1", "Did Not Yet Meet Expectations", "Performance Level 1", True),
        ("level_2", "Partially Met Expectations", "Performance Level 2", False),
        ("level_3", "Approached Expectations", "Performance Level 3", False),
        ("level_4", "Met Expectations", "Performance Level 4", False),
        ("level_5", "Exceeded Expectations", "Performance Level 5", False),
    ]
    missing_metrics = [
        metric_label for _, _, metric_label, _ in tier_specs if metric_label not in performance_by_metric
    ]
    if missing_metrics:
        raise RuntimeError(
            "Missing District of Columbia Grade 3 DCCAPE metrics in OSSE workbook: "
            + ", ".join(sorted(missing_metrics))
        )

    meeting_df = pd.read_excel(raw_path, sheet_name="Meeting, Exceeding", dtype=str).dropna(how="all").copy()
    meeting_row = meeting_df[
        meeting_df["Aggregation Level"].fillna("").astype(str).str.strip().eq("State")
        & meeting_df["Subject"].fillna("").astype(str).str.strip().eq("ELA")
        & meeting_df["Student Group"].fillna("").astype(str).str.strip().eq("All Students")
        & meeting_df["Student Group Value"].fillna("").astype(str).str.strip().eq("All Students")
        & meeting_df["Enrolled Grade or Course"].fillna("").astype(str).str.strip().eq("Grade 3-All")
    ]
    if meeting_row.empty:
        raise RuntimeError(
            "Could not find the District of Columbia statewide Grade 3 ELA Meeting/Exceeding row in the OSSE workbook."
        )

    valid_test_takers = clean_number(meeting_row.iloc[0]["Total Count"])
    proficiency_all_tests_pct = clean_number(meeting_row.iloc[0]["Percent"])
    source_note = (
        "OSSE publishes exact statewide Grade 3 DC CAPE ELA performance levels on the Performance Level sheet. "
        "Those exact tiers are DC CAPE-only; OSSE's separate Meeting/Exceeding tab combines DC CAPE and MSAA, "
        "so its 30.4 percent proficiency figure is slightly above the DC CAPE-only Level 4+5 total."
    )

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, metric_label, is_below_basic) in enumerate(tier_specs, start=1):
        metric_row = performance_by_metric[metric_label]
        rows.append(
            {
                "state": "DC",
                "state_name": "District of Columbia",
                "assessment": "DC CAPE",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": clean_number(metric_row["Percent"]),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Did Not Yet Meet Expectations",
                "source_value_kind": "reported_exact_tier",
                "notes": source_note,
                "source_url": DC_SOURCE_DOWNLOAD_URL,
                "source_page_url": DC_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / DC_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    level_1_pct = clean_number(performance_by_metric["Performance Level 1"]["Percent"])
    level_2_pct = clean_number(performance_by_metric["Performance Level 2"]["Percent"])
    level_3_pct = clean_number(performance_by_metric["Performance Level 3"]["Percent"])
    level_4_pct = clean_number(performance_by_metric["Performance Level 4"]["Percent"])
    level_5_pct = clean_number(performance_by_metric["Performance Level 5"]["Percent"])
    level_4_or_5_pct = None
    if level_4_pct is not None and level_5_pct is not None:
        level_4_or_5_pct = round(level_4_pct + level_5_pct, 2)
    level_3_or_above_pct = None
    if level_3_pct is not None and level_4_pct is not None and level_5_pct is not None:
        level_3_or_above_pct = round(level_3_pct + level_4_pct + level_5_pct, 2)
    level_2_or_above_pct = None
    if level_2_pct is not None and level_3_or_above_pct is not None:
        level_2_or_above_pct = round(level_2_pct + level_3_or_above_pct, 2)

    summary = {
        "state": "DC",
        "state_name": "District of Columbia",
        "assessment": "DC CAPE",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Did Not Yet Meet Expectations",
        "below_basic_analog_pct": level_1_pct,
        "official_statewide_grade3_ela_level2_or_above_pct": level_2_or_above_pct,
        "official_statewide_grade3_ela_level3_or_above_pct": level_3_or_above_pct,
        "official_statewide_grade3_ela_level4_or_5_pct": level_4_or_5_pct,
        "official_statewide_grade3_ela_met_or_exceeded_pct": level_4_or_5_pct,
        "official_valid_test_takers": valid_test_takers,
        "source_notes": (
            source_note
            + f" The companion all-tests Meeting/Exceeding row reports {proficiency_all_tests_pct} percent proficient across DC CAPE plus MSAA."
        ),
        "source_url": DC_SOURCE_DOWNLOAD_URL,
        "source_page_url": DC_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "DC",
        "state_name": "District of Columbia",
        "assessment": "DC CAPE",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Did Not Yet Meet Expectations",
        "source_bin_1_pct": level_1_pct,
        "source_bin_2_label": "Partially Met Expectations",
        "source_bin_2_pct": level_2_pct,
        "source_bin_3_label": "Approached Expectations",
        "source_bin_3_pct": level_3_pct,
        "source_bin_4_label": "Met Expectations",
        "source_bin_4_pct": level_4_pct,
        "source_bin_5_label": "Exceeded Expectations",
        "source_bin_5_pct": level_5_pct,
        "notes": (
            "OSSE publishes exact statewide Grade 3 DC CAPE ELA performance levels directly. "
            "These source bins are from the DC CAPE-only Performance Level sheet."
        ),
        "source_url": DC_SOURCE_DOWNLOAD_URL,
        "source_page_url": DC_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_florida_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=FL_RAW_RELATIVE_PATH,
        source_url=FL_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
        request_headers=FL_DOWNLOAD_HEADERS,
    )

    df = pd.read_excel(raw_path, sheet_name="ELA", header=4, dtype=str, engine="xlrd")
    row = df[
        df["District Number"].fillna("").astype(str).str.strip().eq("00")
        & df["District Name"].fillna("").astype(str).str.strip().eq("STATE TOTALS")
        & df["Grade"].fillna("").astype(str).str.strip().eq("03")
    ]
    if row.empty:
        raise RuntimeError("Could not find the Florida statewide Grade 3 ELA row in the FAST workbook.")

    record = row.iloc[0]
    tier_specs = [
        ("level_1", "Level 1", record[1], True),
        ("level_2", "Level 2", record[2], False),
        ("level_3", "Level 3", record[3], False),
        ("level_4", "Level 4", record[4], False),
        ("level_5", "Level 5", record[5], False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "FL",
                "state_name": "Florida",
                "assessment": "FAST",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": clean_number(value),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Level 1",
                "source_value_kind": "reported_exact_tier",
                "notes": "Florida publishes exact statewide Grade 3 FAST ELA PM3 percentages for Levels 1 through 5 in the district report workbook.",
                "source_url": FL_SOURCE_DOWNLOAD_URL,
                "source_page_url": FL_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / FL_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    level_1_pct = clean_number(record[1])
    level_3_or_above_pct = clean_number(record["Percentage in\n Level 3 or Above"])
    summary = {
        "state": "FL",
        "state_name": "Florida",
        "assessment": "FAST",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Level 1",
        "below_basic_analog_pct": level_1_pct,
        "official_statewide_grade3_ela_level2_or_above_pct": None if level_1_pct is None else round(100.0 - level_1_pct, 2),
        "official_statewide_grade3_ela_level3_or_above_pct": level_3_or_above_pct,
        "source_notes": "Florida publishes exact statewide Grade 3 FAST ELA PM3 percentages for Levels 1 through 5 in the statewide district workbook.",
        "source_url": FL_SOURCE_DOWNLOAD_URL,
        "source_page_url": FL_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "FL",
        "state_name": "Florida",
        "assessment": "FAST",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Level 1",
        "source_bin_1_pct": clean_number(record[1]),
        "source_bin_2_label": "Level 2",
        "source_bin_2_pct": clean_number(record[2]),
        "source_bin_3_label": "Level 3",
        "source_bin_3_pct": clean_number(record[3]),
        "source_bin_4_label": "Level 4",
        "source_bin_4_pct": clean_number(record[4]),
        "source_bin_5_label": "Level 5",
        "source_bin_5_pct": clean_number(record[5]),
        "notes": "Florida publishes exact statewide Grade 3 FAST ELA PM3 Levels 1 through 5 directly.",
        "source_url": FL_SOURCE_DOWNLOAD_URL,
        "source_page_url": FL_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_arkansas_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=AR_RAW_RELATIVE_PATH,
        source_url=AR_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, sheet_name="State")
    row = df[pd.to_numeric(df["Grade"], errors="coerce").eq(3)]
    if row.empty:
        raise RuntimeError("Could not find the Arkansas statewide Grade 3 ELA row in the ATLAS workbook.")

    record = row.iloc[0]
    tier_specs = [
        ("level_1", "Level 1", record["ELA % Level 1"], True),
        ("level_2", "Level 2", record["ELA % Level 2"], False),
        ("level_3", "Level 3", record["ELA % Level 3"], False),
        ("level_4", "Level 4", record["ELA % Level 4"], False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "AR",
                "state_name": "Arkansas",
                "assessment": "ATLAS",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": clean_number(value),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Level 1",
                "source_value_kind": "reported_exact_tier",
                "notes": "Arkansas publishes exact statewide Grade 3 ATLAS ELA performance-level percentages in the annual summary workbook.",
                "source_url": AR_SOURCE_DOWNLOAD_URL,
                "source_page_url": AR_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / AR_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "AR",
        "state_name": "Arkansas",
        "assessment": "ATLAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Level 1",
        "below_basic_analog_pct": clean_number(record["ELA % Level 1"]),
        "official_statewide_grade3_ela_level3_or_4_pct": clean_number(record["ELA % Level 3 & 4"]),
        "source_notes": "Arkansas publishes exact statewide Grade 3 ATLAS ELA performance-level percentages in the annual summary workbook.",
        "source_url": AR_SOURCE_DOWNLOAD_URL,
        "source_page_url": AR_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "AR",
        "state_name": "Arkansas",
        "assessment": "ATLAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Level 1",
        "source_bin_1_pct": clean_number(record["ELA % Level 1"]),
        "source_bin_2_label": "Level 2",
        "source_bin_2_pct": clean_number(record["ELA % Level 2"]),
        "source_bin_3_label": "Level 3",
        "source_bin_3_pct": clean_number(record["ELA % Level 3"]),
        "source_bin_4_label": "Level 4",
        "source_bin_4_pct": clean_number(record["ELA % Level 4"]),
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": "Arkansas publishes exact statewide Grade 3 ATLAS ELA performance tiers directly in the annual summary workbook.",
        "source_url": AR_SOURCE_DOWNLOAD_URL,
        "source_page_url": AR_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_georgia_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=GA_RAW_RELATIVE_PATH,
        source_url=GA_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, sheet_name="State - Grade 3", header=2)
    row = df[pd.to_numeric(df["Unnamed: 0"], errors="coerce").eq(3)]
    if row.empty:
        raise RuntimeError("Could not find the Georgia statewide Grade 3 ELA row in the Georgia Milestones workbook.")

    record = row.iloc[0]
    tier_specs = [
        ("beginning_learner", "Beginning Learner", record["% Beginning Learner"], True),
        ("developing_learner", "Developing Learner", record["% Developing Learner"], False),
        ("proficient_learner", "Proficient Learner", record["% Proficient Learner"], False),
        ("distinguished_learner", "Distinguished Learner", record["% Distinguished Learner"], False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "GA",
                "state_name": "Georgia",
                "assessment": "Georgia Milestones",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": clean_number(value),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Beginning Learner",
                "source_value_kind": "reported_exact_tier",
                "notes": "Georgia publishes exact statewide Grade 3 Georgia Milestones ELA performance-level percentages in the state summary workbook.",
                "source_url": GA_SOURCE_DOWNLOAD_URL,
                "source_page_url": GA_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / GA_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "GA",
        "state_name": "Georgia",
        "assessment": "Georgia Milestones",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Beginning Learner",
        "below_basic_analog_pct": clean_number(record["% Beginning Learner"]),
        "official_statewide_grade3_ela_proficient_or_distinguished_pct": clean_number(record["% Proficient Learner & Above"]),
        "source_notes": "Georgia publishes exact statewide Grade 3 Georgia Milestones ELA performance-level percentages in the state summary workbook.",
        "source_url": GA_SOURCE_DOWNLOAD_URL,
        "source_page_url": GA_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "GA",
        "state_name": "Georgia",
        "assessment": "Georgia Milestones",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Beginning Learner",
        "source_bin_1_pct": clean_number(record["% Beginning Learner"]),
        "source_bin_2_label": "Developing Learner",
        "source_bin_2_pct": clean_number(record["% Developing Learner"]),
        "source_bin_3_label": "Proficient Learner",
        "source_bin_3_pct": clean_number(record["% Proficient Learner"]),
        "source_bin_4_label": "Distinguished Learner",
        "source_bin_4_pct": clean_number(record["% Distinguished Learner"]),
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": "Georgia publishes exact statewide Grade 3 Georgia Milestones ELA performance tiers directly in the state summary workbook.",
        "source_url": GA_SOURCE_DOWNLOAD_URL,
        "source_page_url": GA_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_indiana_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=IN_RAW_RELATIVE_PATH,
        source_url=IN_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, sheet_name="ELA", header=1)
    row = df[df["Statewide"].astype(str).str.strip().eq("Grade 3")]
    if row.empty:
        raise RuntimeError("Could not find the Indiana statewide Grade 3 ELA row in the ILEARN workbook.")

    record = row.iloc[0]
    total_tested = float(record["ELA\nTotal\nTested"])
    if total_tested <= 0:
        raise RuntimeError("Indiana statewide Grade 3 ILEARN workbook reported zero tested students.")
    count_to_pct = lambda value: round((float(value) / total_tested) * 100.0, 2)

    tier_specs = [
        (
            "below_proficiency",
            "Below Proficiency",
            float(record["ELA\nBelow Proficiency"]),
            True,
        ),
        (
            "approaching_proficiency",
            "Approaching Proficiency",
            float(record["ELA \nApproaching Proficiency"]),
            False,
        ),
        (
            "at_proficiency",
            "At Proficiency",
            float(record["ELA \nAt Proficiency"]),
            False,
        ),
        (
            "above_proficiency",
            "Above Proficiency",
            float(record["ELA \nAbove Proficiency"]),
            False,
        ),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, count_value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "IN",
                "state_name": "Indiana",
                "assessment": "ILEARN",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": count_to_pct(count_value),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Below Proficiency",
                "source_value_kind": "derived_exact_tier_from_published_counts",
                "notes": (
                    "Indiana publishes statewide Grade 3 ILEARN counts by performance level. "
                    "Percentages here are derived from those published counts and total tested."
                ),
                "source_url": IN_SOURCE_DOWNLOAD_URL,
                "source_page_url": IN_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / IN_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    proficient_pct = round(float(record["ELA\nProficient \n%"]) * 100.0, 2)
    summary = {
        "state": "IN",
        "state_name": "Indiana",
        "assessment": "ILEARN",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Below Proficiency",
        "below_basic_analog_pct": count_to_pct(record["ELA\nBelow Proficiency"]),
        "official_statewide_grade3_ela_at_or_above_proficiency_pct": proficient_pct,
        "source_notes": "Indiana publishes statewide Grade 3 ILEARN counts by performance level in the statewide summary workbook.",
        "source_url": IN_SOURCE_DOWNLOAD_URL,
        "source_page_url": IN_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "IN",
        "state_name": "Indiana",
        "assessment": "ILEARN",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_counts_by_exact_tier",
        "source_bin_1_label": "Below Proficiency",
        "source_bin_1_pct": count_to_pct(record["ELA\nBelow Proficiency"]),
        "source_bin_2_label": "Approaching Proficiency",
        "source_bin_2_pct": count_to_pct(record["ELA \nApproaching Proficiency"]),
        "source_bin_3_label": "At Proficiency",
        "source_bin_3_pct": count_to_pct(record["ELA \nAt Proficiency"]),
        "source_bin_4_label": "Above Proficiency",
        "source_bin_4_pct": count_to_pct(record["ELA \nAbove Proficiency"]),
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": "Indiana publishes statewide counts for each Grade 3 ILEARN performance level; percentages here are derived from those counts.",
        "source_url": IN_SOURCE_DOWNLOAD_URL,
        "source_page_url": IN_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_new_jersey_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=NJ_RAW_RELATIVE_PATH,
        source_url=NJ_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, sheet_name="ELA03", header=2, dtype=str)
    row = df[
        df["County Code"].fillna("").astype(str).str.strip().eq("State")
        & df["Subgroup"].fillna("").astype(str).str.strip().eq("Total")
    ]
    if row.empty:
        raise RuntimeError("Could not find the New Jersey statewide Grade 3 ELA row in the NJSLA workbook.")

    record = row.iloc[0]
    tier_specs = [
        ("level_1", "Level 1", record["L1 Percent"], True),
        ("level_2", "Level 2", record["L2 Percent"], False),
        ("level_3", "Level 3", record["L3 Percent"], False),
        ("level_4", "Level 4", record["L4 Percent"], False),
        ("level_5", "Level 5", record["L5 Percent"], False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "NJ",
                "state_name": "New Jersey",
                "assessment": "NJSLA",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": clean_number(value),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Level 1",
                "source_value_kind": "reported_exact_tier",
                "notes": "New Jersey publishes exact statewide Grade 3 NJSLA ELA performance-level percentages in the spring results workbook.",
                "source_url": NJ_SOURCE_DOWNLOAD_URL,
                "source_page_url": NJ_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / NJ_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "NJ",
        "state_name": "New Jersey",
        "assessment": "NJSLA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Level 1",
        "below_basic_analog_pct": clean_number(record["L1 Percent"]),
        "official_statewide_grade3_ela_level4_or_5_pct": round(
            (clean_number(record["L4 Percent"]) or 0.0) + (clean_number(record["L5 Percent"]) or 0.0),
            2,
        ),
        "source_notes": "New Jersey publishes exact statewide Grade 3 NJSLA ELA performance-level percentages in the spring results workbook.",
        "source_url": NJ_SOURCE_DOWNLOAD_URL,
        "source_page_url": NJ_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "NJ",
        "state_name": "New Jersey",
        "assessment": "NJSLA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Level 1",
        "source_bin_1_pct": clean_number(record["L1 Percent"]),
        "source_bin_2_label": "Level 2",
        "source_bin_2_pct": clean_number(record["L2 Percent"]),
        "source_bin_3_label": "Level 3",
        "source_bin_3_pct": clean_number(record["L3 Percent"]),
        "source_bin_4_label": "Level 4",
        "source_bin_4_pct": clean_number(record["L4 Percent"]),
        "source_bin_5_label": "Level 5",
        "source_bin_5_pct": clean_number(record["L5 Percent"]),
        "notes": "New Jersey publishes exact statewide Grade 3 NJSLA ELA performance tiers directly in the spring workbook.",
        "source_url": NJ_SOURCE_DOWNLOAD_URL,
        "source_page_url": NJ_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_new_york_tiers(repo_root: Path) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    source_note = (
        "NYSED Data Site's 2024-25 Report Card Database publishes All Public Schools statewide Grade 3 ELA counts and "
        "tested percentages for Levels 1 through 4 in the Annual EM ELA table."
    )
    tier_specs = [
        ("level_1", "Level 1", 20.0, True),
        ("level_2", "Level 2", 26.0, False),
        ("level_3", "Level 3", 33.0, False),
        ("level_4", "Level 4", 22.0, False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "NY",
                "state_name": "New York",
                "assessment": "Grades 3-8 ELA",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Level 1",
                "source_value_kind": "reported_exact_tier",
                "notes": source_note,
                "source_url": NY_SOURCE_DOWNLOAD_URL,
                "source_page_url": NY_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / NY_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "NY",
        "state_name": "New York",
        "assessment": "Grades 3-8 ELA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Level 1",
        "below_basic_analog_pct": 20.0,
        "official_statewide_grade3_ela_level3_or_4_pct": 54.0,
        "official_total_students": 185763,
        "official_valid_test_takers": 161336,
        "official_not_tested": 24427,
        "source_notes": source_note,
        "source_url": NY_SOURCE_DOWNLOAD_URL,
        "source_page_url": NY_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "NY",
        "state_name": "New York",
        "assessment": "Grades 3-8 ELA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Level 1",
        "source_bin_1_pct": 20.0,
        "source_bin_2_label": "Level 2",
        "source_bin_2_pct": 26.0,
        "source_bin_3_label": "Level 3",
        "source_bin_3_pct": 33.0,
        "source_bin_4_label": "Level 4",
        "source_bin_4_pct": 22.0,
        "source_bin_5_label": "Level 3 or 4",
        "source_bin_5_pct": 54.0,
        "notes": (
            "These are New York's published All Public Schools statewide Grade 3 ELA source bins from the "
            "2024-25 Report Card Database, using tested-student percentages."
        ),
        "source_url": NY_SOURCE_DOWNLOAD_URL,
        "source_page_url": NY_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_kentucky_tiers(repo_root: Path) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    tier_specs = [
        ("novice", "Novice", 24.8, True),
        ("apprentice", "Apprentice", 28.3, False),
        ("proficient", "Proficient", 28.8, False),
        ("distinguished", "Distinguished", 18.1, False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "KY",
                "state_name": "Kentucky",
                "assessment": "KSA",
                "subject": "ELA",
                "subject_label": "Reading",
                "grade": "03",
                "school_year": "2023-2024",
                "administration_year": 2024,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Novice",
                "source_value_kind": "reported_exact_tier",
                "notes": "Kentucky publishes exact statewide Grade 3 Reading performance-level percentages in the KSA yearbook.",
                "source_url": KY_SOURCE_DOWNLOAD_URL,
                "source_page_url": KY_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / KY_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "KY",
        "state_name": "Kentucky",
        "assessment": "KSA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2023-2024",
        "administration_year": 2024,
        "below_basic_analog_label": "Novice",
        "below_basic_analog_pct": 24.8,
        "official_statewide_grade3_reading_proficient_or_distinguished_pct": 46.9,
        "source_notes": "Kentucky publishes exact Grade 3 Reading performance-level percentages in the KSA yearbook.",
        "source_url": KY_SOURCE_DOWNLOAD_URL,
        "source_page_url": KY_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "KY",
        "state_name": "Kentucky",
        "assessment": "KSA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2023-2024",
        "administration_year": 2024,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Novice",
        "source_bin_1_pct": 24.8,
        "source_bin_2_label": "Apprentice",
        "source_bin_2_pct": 28.3,
        "source_bin_3_label": "Proficient",
        "source_bin_3_pct": 28.8,
        "source_bin_4_label": "Distinguished",
        "source_bin_4_pct": 18.1,
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": "Kentucky publishes exact statewide Grade 3 Reading performance tiers directly in the KSA yearbook.",
        "source_url": KY_SOURCE_DOWNLOAD_URL,
        "source_page_url": KY_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_louisiana_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=LA_RAW_RELATIVE_PATH,
        source_url=LA_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, sheet_name="Grade 03", header=8, dtype=str)
    row = df[df["Unnamed: 0"].fillna("").astype(str).str.strip().eq("STATE")]
    if row.empty:
        raise RuntimeError("Could not find the Louisiana statewide Grade 3 ELA row in the LEAP workbook.")

    record = row.iloc[0]
    tier_specs = [
        ("unsatisfactory", "Unsatisfactory", record["U"], True),
        ("approaching_basic", "Approaching Basic", record["AB"], False),
        ("basic", "Basic", record["B"], False),
        ("mastery", "Mastery", record["M"], False),
        ("advanced", "Advanced", record["A"], False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "LA",
                "state_name": "Louisiana",
                "assessment": "LEAP",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": clean_number(value),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Unsatisfactory",
                "source_value_kind": "reported_exact_tier",
                "notes": "Louisiana publishes exact statewide Grade 3 LEAP ELA achievement-level percentages in the State LEA achievement summary workbook.",
                "source_url": LA_SOURCE_DOWNLOAD_URL,
                "source_page_url": LA_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / LA_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    mastery_or_advanced = round((clean_number(record["M"]) or 0.0) + (clean_number(record["A"]) or 0.0), 2)
    summary = {
        "state": "LA",
        "state_name": "Louisiana",
        "assessment": "LEAP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Unsatisfactory",
        "below_basic_analog_pct": clean_number(record["U"]),
        "official_statewide_grade3_ela_mastery_or_advanced_pct": mastery_or_advanced,
        "source_notes": "Louisiana publishes exact statewide Grade 3 LEAP ELA achievement-level percentages in the State LEA achievement summary workbook.",
        "source_url": LA_SOURCE_DOWNLOAD_URL,
        "source_page_url": LA_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "LA",
        "state_name": "Louisiana",
        "assessment": "LEAP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Unsatisfactory",
        "source_bin_1_pct": clean_number(record["U"]),
        "source_bin_2_label": "Approaching Basic",
        "source_bin_2_pct": clean_number(record["AB"]),
        "source_bin_3_label": "Basic",
        "source_bin_3_pct": clean_number(record["B"]),
        "source_bin_4_label": "Mastery",
        "source_bin_4_pct": clean_number(record["M"]),
        "source_bin_5_label": "Advanced",
        "source_bin_5_pct": clean_number(record["A"]),
        "notes": "Louisiana publishes exact statewide Grade 3 LEAP ELA achievement levels directly.",
        "source_url": LA_SOURCE_DOWNLOAD_URL,
        "source_page_url": LA_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_mississippi_tiers(repo_root: Path) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    tier_specs = [
        ("minimal", "Minimal", 10.7, True),
        ("basic", "Basic", 13.7, False),
        ("pass", "Pass", 26.3, False),
        ("proficient", "Proficient", 35.5, False),
        ("advanced", "Advanced", 13.9, False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "MS",
                "state_name": "Mississippi",
                "assessment": "MAAP",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Minimal",
                "source_value_kind": "reported_exact_tier",
                "notes": "Mississippi publishes exact statewide Grade 3 MAAP ELA performance-level percentages in the 2025 executive summary PDF.",
                "source_url": MS_SOURCE_DOWNLOAD_URL,
                "source_page_url": MS_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / MS_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "MS",
        "state_name": "Mississippi",
        "assessment": "MAAP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Minimal",
        "below_basic_analog_pct": 10.7,
        "official_statewide_grade3_ela_proficient_or_advanced_pct": 49.3,
        "source_notes": "Mississippi publishes exact statewide Grade 3 MAAP ELA performance-level percentages in the 2025 executive summary PDF.",
        "source_url": MS_SOURCE_DOWNLOAD_URL,
        "source_page_url": MS_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "MS",
        "state_name": "Mississippi",
        "assessment": "MAAP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Minimal",
        "source_bin_1_pct": 10.7,
        "source_bin_2_label": "Basic",
        "source_bin_2_pct": 13.7,
        "source_bin_3_label": "Pass",
        "source_bin_3_pct": 26.3,
        "source_bin_4_label": "Proficient",
        "source_bin_4_pct": 35.5,
        "source_bin_5_label": "Advanced",
        "source_bin_5_pct": 13.9,
        "notes": "Mississippi publishes exact statewide Grade 3 MAAP ELA performance levels directly in the executive summary PDF.",
        "source_url": MS_SOURCE_DOWNLOAD_URL,
        "source_page_url": MS_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_south_carolina_tiers(repo_root: Path) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    tier_specs = [
        ("does_not_meet_expectations", "Does Not Meet Expectations", 14.4, True),
        ("approaches_expectations", "Approaches Expectations", 23.8, False),
        ("meets_expectations", "Meets Expectations", 30.8, False),
        ("exceeds_expectations", "Exceeds Expectations", 31.0, False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "SC",
                "state_name": "South Carolina",
                "assessment": "SC READY",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Does Not Meet Expectations",
                "source_value_kind": "reported_exact_tier",
                "notes": "South Carolina publishes exact statewide Grade 3 SC READY ELA performance-level percentages on the public state results page.",
                "source_url": SC_SOURCE_DOWNLOAD_URL,
                "source_page_url": SC_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / SC_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "SC",
        "state_name": "South Carolina",
        "assessment": "SC READY",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Does Not Meet Expectations",
        "below_basic_analog_pct": 14.4,
        "official_statewide_grade3_ela_meets_or_exceeds_pct": 61.7,
        "source_notes": "South Carolina publishes exact statewide Grade 3 SC READY ELA performance-level percentages on the public state results page.",
        "source_url": SC_SOURCE_DOWNLOAD_URL,
        "source_page_url": SC_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "SC",
        "state_name": "South Carolina",
        "assessment": "SC READY",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Does Not Meet Expectations",
        "source_bin_1_pct": 14.4,
        "source_bin_2_label": "Approaches Expectations",
        "source_bin_2_pct": 23.8,
        "source_bin_3_label": "Meets Expectations",
        "source_bin_3_pct": 30.8,
        "source_bin_4_label": "Exceeds Expectations",
        "source_bin_4_pct": 31.0,
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": "South Carolina publishes exact statewide Grade 3 SC READY ELA performance tiers directly on the state results page.",
        "source_url": SC_SOURCE_DOWNLOAD_URL,
        "source_page_url": SC_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_tennessee_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=TN_RAW_RELATIVE_PATH,
        source_url=TN_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, dtype=str)
    row = df[
        df["system"].fillna("").astype(str).str.strip().eq("0")
        & df["student_group"].fillna("").astype(str).str.strip().eq("All Students")
        & df["test"].fillna("").astype(str).str.strip().eq("ACH")
        & df["subject"].fillna("").astype(str).str.strip().eq("ELA")
        & df["grade"].fillna("").astype(str).str.strip().eq("3")
    ]
    if row.empty:
        raise RuntimeError("Could not find the Tennessee statewide Grade 3 ELA row in the TCAP workbook.")

    record = row.iloc[0]
    tier_specs = [
        ("below", "Below", record["pct_below"], True),
        ("approaching", "Approaching", record["pct_approaching"], False),
        ("met_expectations", "Met Expectations", record["pct_met_expectations"], False),
        ("exceeded_expectations", "Exceeded Expectations", record["pct_exceeded_expectations"], False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "TN",
                "state_name": "Tennessee",
                "assessment": "TCAP",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": clean_number(value),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Below",
                "source_value_kind": "reported_exact_tier",
                "notes": "Tennessee publishes exact statewide Grade 3 TCAP ELA tier percentages in the state assessment file.",
                "source_url": TN_SOURCE_DOWNLOAD_URL,
                "source_page_url": TN_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / TN_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "TN",
        "state_name": "Tennessee",
        "assessment": "TCAP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Below",
        "below_basic_analog_pct": clean_number(record["pct_below"]),
        "official_statewide_grade3_ela_met_or_exceeded_pct": clean_number(record["pct_met_exceeded"]),
        "source_notes": "Tennessee publishes exact statewide Grade 3 TCAP ELA tier percentages in the state assessment file.",
        "source_url": TN_SOURCE_DOWNLOAD_URL,
        "source_page_url": TN_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "TN",
        "state_name": "Tennessee",
        "assessment": "TCAP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Below",
        "source_bin_1_pct": clean_number(record["pct_below"]),
        "source_bin_2_label": "Approaching",
        "source_bin_2_pct": clean_number(record["pct_approaching"]),
        "source_bin_3_label": "Met Expectations",
        "source_bin_3_pct": clean_number(record["pct_met_expectations"]),
        "source_bin_4_label": "Exceeded Expectations",
        "source_bin_4_pct": clean_number(record["pct_exceeded_expectations"]),
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": "Tennessee publishes exact statewide Grade 3 TCAP ELA performance tiers directly.",
        "source_url": TN_SOURCE_DOWNLOAD_URL,
        "source_page_url": TN_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_texas_field_guide(repo_root: Path) -> None:
    rows = [
        {
            "raw_field_name": "DDA03ARE1S24R",
            "geography_level": "district",
            "student_group": "all_students",
            "grade": "03",
            "subject": "reading_language_arts",
            "metric_label": "Approaches Grade Level or above",
            "value_kind": "cumulative_threshold",
            "plain_english": "Percent of all tested Grade 3 students in the district who scored at Approaches Grade Level or above in RLA in 2024.",
        },
        {
            "raw_field_name": "DDA03ARE1224R",
            "geography_level": "district",
            "student_group": "all_students",
            "grade": "03",
            "subject": "reading_language_arts",
            "metric_label": "Meets Grade Level or above",
            "value_kind": "cumulative_threshold",
            "plain_english": "Percent of all tested Grade 3 students in the district who scored at Meets Grade Level or above in RLA in 2024.",
        },
        {
            "raw_field_name": "DDA03ARE1324R",
            "geography_level": "district",
            "student_group": "all_students",
            "grade": "03",
            "subject": "reading_language_arts",
            "metric_label": "Masters Grade Level",
            "value_kind": "top_tier_exact",
            "plain_english": "Percent of all tested Grade 3 students in the district who scored at Masters Grade Level in RLA in 2024.",
        },
        {
            "raw_field_name": "DDA03AMA1S24R",
            "geography_level": "district",
            "student_group": "all_students",
            "grade": "03",
            "subject": "mathematics",
            "metric_label": "Approaches Grade Level or above",
            "value_kind": "cumulative_threshold",
            "plain_english": "Percent of all tested Grade 3 students in the district who scored at Approaches Grade Level or above in math in 2024.",
        },
        {
            "raw_field_name": "DDA03AMA1224R",
            "geography_level": "district",
            "student_group": "all_students",
            "grade": "03",
            "subject": "mathematics",
            "metric_label": "Meets Grade Level or above",
            "value_kind": "cumulative_threshold",
            "plain_english": "Percent of all tested Grade 3 students in the district who scored at Meets Grade Level or above in math in 2024.",
        },
        {
            "raw_field_name": "DDA03AMA1324R",
            "geography_level": "district",
            "student_group": "all_students",
            "grade": "03",
            "subject": "mathematics",
            "metric_label": "Masters Grade Level",
            "value_kind": "top_tier_exact",
            "plain_english": "Percent of all tested Grade 3 students in the district who scored at Masters Grade Level in math in 2024.",
        },
        {
            "raw_field_name": "SDA03ARE1S24R",
            "geography_level": "state",
            "student_group": "all_students",
            "grade": "03",
            "subject": "reading_language_arts",
            "metric_label": "Approaches Grade Level or above",
            "value_kind": "cumulative_threshold",
            "plain_english": "Percent of all tested Grade 3 students statewide who scored at Approaches Grade Level or above in RLA in 2024.",
        },
        {
            "raw_field_name": "SDA03ARE1224R",
            "geography_level": "state",
            "student_group": "all_students",
            "grade": "03",
            "subject": "reading_language_arts",
            "metric_label": "Meets Grade Level or above",
            "value_kind": "cumulative_threshold",
            "plain_english": "Percent of all tested Grade 3 students statewide who scored at Meets Grade Level or above in RLA in 2024.",
        },
        {
            "raw_field_name": "SDA03ARE1324R",
            "geography_level": "state",
            "student_group": "all_students",
            "grade": "03",
            "subject": "reading_language_arts",
            "metric_label": "Masters Grade Level",
            "value_kind": "top_tier_exact",
            "plain_english": "Percent of all tested Grade 3 students statewide who scored at Masters Grade Level in RLA in 2024.",
        },
        {
            "raw_field_name": "SDA03AMA1S24R",
            "geography_level": "state",
            "student_group": "all_students",
            "grade": "03",
            "subject": "mathematics",
            "metric_label": "Approaches Grade Level or above",
            "value_kind": "cumulative_threshold",
            "plain_english": "Percent of all tested Grade 3 students statewide who scored at Approaches Grade Level or above in math in 2024.",
        },
        {
            "raw_field_name": "SDA03AMA1224R",
            "geography_level": "state",
            "student_group": "all_students",
            "grade": "03",
            "subject": "mathematics",
            "metric_label": "Meets Grade Level or above",
            "value_kind": "cumulative_threshold",
            "plain_english": "Percent of all tested Grade 3 students statewide who scored at Meets Grade Level or above in math in 2024.",
        },
        {
            "raw_field_name": "SDA03AMA1324R",
            "geography_level": "state",
            "student_group": "all_students",
            "grade": "03",
            "subject": "mathematics",
            "metric_label": "Masters Grade Level",
            "value_kind": "top_tier_exact",
            "plain_english": "Percent of all tested Grade 3 students statewide who scored at Masters Grade Level in math in 2024.",
        },
    ]
    output_path = repo_root / TX_FIELD_GUIDE_RELATIVE_PATH
    ensure_parent(output_path)
    pd.DataFrame(rows).to_csv(output_path, index=False)


def _build_texas_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=TX_RAW_RELATIVE_PATH,
        source_url=TX_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )
    _build_texas_field_guide(repo_root)

    df = pd.read_excel(raw_path, dtype=str)
    if df.empty:
        raise RuntimeError("Texas statewide Grade 3 STAAR workbook was empty.")
    record = df.iloc[0]

    approaches_or_above = clean_number(record["SDA03ARE1S24R"])
    meets_or_above = clean_number(record["SDA03ARE1224R"])
    masters = clean_number(record["SDA03ARE1324R"])
    if approaches_or_above is None or meets_or_above is None or masters is None:
        raise RuntimeError("Texas statewide Grade 3 STAAR workbook was missing expected RLA fields.")

    tiers = [
        ("did_not_meet_grade_level", "Did Not Meet Grade Level", 100.0 - approaches_or_above, True),
        (
            "approaches_grade_level_only",
            "Approaches Grade Level Only",
            approaches_or_above - meets_or_above,
            False,
        ),
        ("meets_grade_level_only", "Meets Grade Level Only", meets_or_above - masters, False),
        ("masters_grade_level", "Masters Grade Level", masters, False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tiers, start=1):
        rows.append(
            {
                "state": "TX",
                "state_name": "Texas",
                "assessment": "STAAR",
                "subject": "ELA",
                "subject_label": "Reading Language Arts",
                "grade": "03",
                "school_year": "2023-2024",
                "administration_year": 2024,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Did Not Meet Grade Level",
                "source_value_kind": "derived_exact_tier_from_cumulative_thresholds",
                "notes": (
                    "Texas reports Approaches-or-above, Meets-or-above, and Masters. "
                    "Exact tiers here are derived as: did_not_meet = 100 - approaches; "
                    "approaches_only = approaches - meets; meets_only = meets - masters."
                ),
                "source_url": TX_SOURCE_DOWNLOAD_URL,
                "source_page_url": TX_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / TX_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "TX",
        "state_name": "Texas",
        "assessment": "STAAR",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2023-2024",
        "administration_year": 2024,
        "below_basic_analog_label": "Did Not Meet Grade Level",
        "below_basic_analog_pct": 100.0 - approaches_or_above,
        "official_statewide_grade3_rla_approaches_or_above_pct": approaches_or_above,
        "official_statewide_grade3_rla_meets_or_above_pct": meets_or_above,
        "official_statewide_grade3_rla_masters_pct": masters,
        "source_notes": (
            "Texas publishes cumulative threshold rates, so exact tiers are derived by subtraction "
            "from the statewide TAPR Grade 3 STAAR export."
        ),
        "source_url": TX_SOURCE_DOWNLOAD_URL,
        "source_page_url": TX_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "TX",
        "state_name": "Texas",
        "assessment": "STAAR",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2023-2024",
        "administration_year": 2024,
        "source_bin_structure": "published_cumulative_thresholds",
        "source_bin_1_label": "Approaches Grade Level or above",
        "source_bin_1_pct": approaches_or_above,
        "source_bin_2_label": "Meets Grade Level or above",
        "source_bin_2_pct": meets_or_above,
        "source_bin_3_label": "Masters Grade Level",
        "source_bin_3_pct": masters,
        "source_bin_4_label": "",
        "source_bin_4_pct": None,
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": "Texas publishes cumulative thresholds rather than exact tiers; these are the original statewide source bins.",
        "source_url": TX_SOURCE_DOWNLOAD_URL,
        "source_page_url": TX_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_washington_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_csv: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=WA_RAW_RELATIVE_PATH,
        source_url=WA_SOURCE_DOWNLOAD_URL,
        local_override=raw_csv,
    )

    df = pd.read_csv(raw_path, dtype=str)
    row = df[
        df["schoolyear"].fillna("").astype(str).str.strip().eq("2024-25")
        & df["organizationlevel"].fillna("").astype(str).str.strip().eq("State")
        & df["districtname"].fillna("").astype(str).str.strip().eq("State Total")
        & df["studentgroup"].fillna("").astype(str).str.strip().eq("All Students")
        & df["gradelevel"].fillna("").astype(str).str.strip().eq("03")
        & df["testadministration"].fillna("").astype(str).str.strip().eq("SBAC")
        & df["testsubject"].fillna("").astype(str).str.strip().eq("ELA")
    ]
    if row.empty:
        raise RuntimeError("Could not find the Washington statewide Grade 3 ELA row in the SBAC extract.")

    record = row.iloc[0]
    participation = clean_number(record["percent_participation"])
    if participation in {None, 0}:
        raise RuntimeError("Washington SBAC statewide row was missing participation needed for tested-only renormalization.")

    def renormalize_tested_only(column: str) -> float:
        value = clean_number(record[column])
        if value is None:
            raise RuntimeError(f"Washington SBAC statewide row was missing {column}.")
        return round((value / participation) * 100.0, 2)

    tier_specs = [
        ("level_1", "Level 1", renormalize_tested_only("percentlevel1"), True),
        ("level_2", "Level 2", renormalize_tested_only("percentlevel2"), False),
        ("level_3", "Level 3", renormalize_tested_only("percentlevel3"), False),
        ("level_4", "Level 4", renormalize_tested_only("percentlevel4"), False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "WA",
                "state_name": "Washington",
                "assessment": "SBAC",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Level 1",
                "source_value_kind": "derived_exact_tier_from_tested_only_renormalization",
                "notes": (
                    "Washington publishes statewide Grade 3 SBAC ELA level shares as fractions of all expected students. "
                    "These exact tiers are renormalized here on a tested-only denominator by dividing each level share by participation."
                ),
                "source_url": WA_SOURCE_DOWNLOAD_URL,
                "source_page_url": WA_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / WA_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "WA",
        "state_name": "Washington",
        "assessment": "SBAC",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Level 1",
        "below_basic_analog_pct": renormalize_tested_only("percentlevel1"),
        "official_statewide_grade3_ela_level3_or_4_tested_only_pct": round(
            renormalize_tested_only("percentlevel3") + renormalize_tested_only("percentlevel4"),
            2,
        ),
        "source_notes": (
            "Washington publishes statewide Grade 3 SBAC ELA level shares as fractions of all expected students, "
            "so the exact tier percentages here are renormalized on a tested-only denominator."
        ),
        "source_url": WA_SOURCE_DOWNLOAD_URL,
        "source_page_url": WA_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "WA",
        "state_name": "Washington",
        "assessment": "SBAC",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_levels_plus_no_score",
        "source_bin_1_label": "Level 1",
        "source_bin_1_pct": round((clean_number(record["percentlevel1"]) or 0.0) * 100.0, 2),
        "source_bin_2_label": "Level 2",
        "source_bin_2_pct": round((clean_number(record["percentlevel2"]) or 0.0) * 100.0, 2),
        "source_bin_3_label": "Level 3",
        "source_bin_3_pct": round((clean_number(record["percentlevel3"]) or 0.0) * 100.0, 2),
        "source_bin_4_label": "Level 4",
        "source_bin_4_pct": round((clean_number(record["percentlevel4"]) or 0.0) * 100.0, 2),
        "source_bin_5_label": "No Score",
        "source_bin_5_pct": round((clean_number(record["percent_no_score"]) or 0.0) * 100.0, 2),
        "notes": (
            "These are Washington's original published statewide Grade 3 SBAC ELA source bins, reported as shares of all expected students."
        ),
        "source_url": WA_SOURCE_DOWNLOAD_URL,
        "source_page_url": WA_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_wisconsin_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_zip: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=WI_RAW_RELATIVE_PATH,
        source_url=WI_SOURCE_DOWNLOAD_URL,
        local_override=raw_zip,
    )

    with zipfile.ZipFile(raw_path) as archive:
        target_name = next(
            (name for name in archive.namelist() if "forward_certified_ELA_RDG_WRT_2024-25.csv" in name),
            None,
        )
        if target_name is None:
            raise RuntimeError("Could not find the Wisconsin Forward ELA CSV inside the certified download zip.")
        df = pd.read_csv(archive.open(target_name), dtype=str)

    rows = df[
        df["DISTRICT_NAME"].fillna("").astype(str).str.strip().eq("[Statewide]")
        & df["SCHOOL_NAME"].fillna("").astype(str).str.strip().eq("[Statewide]")
        & df["TEST_SUBJECT"].fillna("").astype(str).str.strip().eq("ELA")
        & df["GRADE_LEVEL"].fillna("").astype(str).str.strip().eq("3")
        & df["TEST_GROUP"].fillna("").astype(str).str.strip().eq("Forward")
        & df["GROUP_BY"].fillna("").astype(str).str.strip().eq("All Students")
        & df["GROUP_BY_VALUE"].fillna("").astype(str).str.strip().eq("All Students")
    ]
    if rows.empty:
        raise RuntimeError("Could not find the Wisconsin statewide Grade 3 ELA rows in the Forward certified CSV.")

    counts = {str(row["TEST_RESULT"]).strip(): float(row["STUDENT_COUNT"]) for _, row in rows.iterrows()}
    tested = sum(value for label, value in counts.items() if label != "No Test")
    if tested <= 0:
        raise RuntimeError("Wisconsin Forward statewide Grade 3 ELA rows reported zero tested students.")

    def tested_only_pct(label: str) -> float:
        value = counts.get(label)
        if value is None:
            raise RuntimeError(f"Wisconsin Forward statewide Grade 3 ELA rows were missing {label}.")
        return round((value / tested) * 100.0, 2)

    tier_specs = [
        ("developing", "Developing", tested_only_pct("Developing"), True),
        ("approaching", "Approaching", tested_only_pct("Approaching"), False),
        ("meeting", "Meeting", tested_only_pct("Meeting"), False),
        ("advanced", "Advanced", tested_only_pct("Advanced"), False),
    ]

    tier_rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        tier_rows.append(
            {
                "state": "WI",
                "state_name": "Wisconsin",
                "assessment": "Forward Exam",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Developing",
                "source_value_kind": "derived_exact_tier_from_tested_only_renormalization",
                "notes": (
                    "Wisconsin publishes statewide Grade 3 Forward ELA percentages on a denominator that includes No Test. "
                    "These exact tiers are renormalized here on a tested-only denominator."
                ),
                "source_url": WI_SOURCE_DOWNLOAD_URL,
                "source_page_url": WI_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(tier_rows)
    output_path = repo_root / WI_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "WI",
        "state_name": "Wisconsin",
        "assessment": "Forward Exam",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Developing",
        "below_basic_analog_pct": tested_only_pct("Developing"),
        "official_statewide_grade3_ela_meeting_or_advanced_tested_only_pct": round(
            tested_only_pct("Meeting") + tested_only_pct("Advanced"),
            2,
        ),
        "source_notes": (
            "Wisconsin publishes statewide Grade 3 Forward ELA percentages on a denominator that includes No Test, "
            "so the exact tier percentages here are renormalized on a tested-only denominator."
        ),
        "source_url": WI_SOURCE_DOWNLOAD_URL,
        "source_page_url": WI_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "WI",
        "state_name": "Wisconsin",
        "assessment": "Forward Exam",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_bins_with_no_test_in_denominator",
        "source_bin_1_label": "Developing",
        "source_bin_1_pct": clean_number(rows.loc[rows["TEST_RESULT"].eq("Developing"), "PERCENT_OF_GROUP"].iloc[0]),
        "source_bin_2_label": "Approaching",
        "source_bin_2_pct": clean_number(rows.loc[rows["TEST_RESULT"].eq("Approaching"), "PERCENT_OF_GROUP"].iloc[0]),
        "source_bin_3_label": "Meeting",
        "source_bin_3_pct": clean_number(rows.loc[rows["TEST_RESULT"].eq("Meeting"), "PERCENT_OF_GROUP"].iloc[0]),
        "source_bin_4_label": "Advanced",
        "source_bin_4_pct": clean_number(rows.loc[rows["TEST_RESULT"].eq("Advanced"), "PERCENT_OF_GROUP"].iloc[0]),
        "source_bin_5_label": "No Test",
        "source_bin_5_pct": clean_number(rows.loc[rows["TEST_RESULT"].eq("No Test"), "PERCENT_OF_GROUP"].iloc[0]),
        "notes": "These are Wisconsin's original published statewide Grade 3 Forward ELA source bins before tested-only renormalization.",
        "source_url": WI_SOURCE_DOWNLOAD_URL,
        "source_page_url": WI_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_delaware_public_reference(repo_root: Path) -> tuple[dict[str, object], dict[str, object]]:
    summary = {
        "state": "DE",
        "state_name": "Delaware",
        "assessment": "Smarter Balanced",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "100 - Met Achievement Standard",
        "below_basic_analog_pct": 61.28,
        "official_statewide_grade3_ela_met_achievement_standard_pct": 38.72,
        "source_notes": (
            "Delaware's public statewide Grade 3 ELA rows expose a proficiency figure but not the full statewide "
            "performance-level split, so the below-basic analog is filled as 100 - Met Achievement Standard."
        ),
        "source_url": DE_SOURCE_DOWNLOAD_URL,
        "source_page_url": DE_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "DE",
        "state_name": "Delaware",
        "assessment": "Smarter Balanced",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_proficiency_only",
        "source_bin_1_label": "Met Achievement Standard (proficient)",
        "source_bin_1_pct": 38.72,
        "source_bin_2_label": "",
        "source_bin_2_pct": None,
        "source_bin_3_label": "",
        "source_bin_3_pct": None,
        "source_bin_4_label": "",
        "source_bin_4_pct": None,
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": (
            "The public Delaware statewide assessment rows used here expose Grade 3 ELA proficiency only, not a full statewide tier split."
        ),
        "source_url": DE_SOURCE_DOWNLOAD_URL,
        "source_page_url": DE_SOURCE_PAGE_URL,
    }
    _write_single_row_csv(repo_root, DE_OUTPUT_RELATIVE_PATH, published_reference)
    return summary, published_reference


def _build_new_hampshire_public_reference(repo_root: Path) -> tuple[dict[str, object], dict[str, object]]:
    source_note = (
        "New Hampshire's official iPlatform assessment report publishes the statewide 2025 Grade 3 NH SAS ELA "
        "proficiency rate. The public result used here exposes proficiency, not the full four-level statewide split."
    )
    summary = {
        "state": "NH",
        "state_name": "New Hampshire",
        "assessment": "NH SAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "100 - Percent Proficient",
        "below_basic_analog_pct": 51.0,
        "official_statewide_grade3_ela_percent_proficient_pct": 49.0,
        "source_notes": (
            source_note
            + " The below-basic analog remains a not-proficient proxy defined here as 100 - Percent Proficient."
        ),
        "source_url": NH_SOURCE_DOWNLOAD_URL,
        "source_page_url": NH_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "NH",
        "state_name": "New Hampshire",
        "assessment": "NH SAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_proficiency_only",
        "source_bin_1_label": "Percent Proficient",
        "source_bin_1_pct": 49.0,
        "source_bin_2_label": "",
        "source_bin_2_pct": None,
        "source_bin_3_label": "",
        "source_bin_3_pct": None,
        "source_bin_4_label": "",
        "source_bin_4_pct": None,
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": source_note,
        "source_url": NH_SOURCE_DOWNLOAD_URL,
        "source_page_url": NH_SOURCE_PAGE_URL,
    }
    _write_single_row_csv(repo_root, NH_OUTPUT_RELATIVE_PATH, published_reference)
    return summary, published_reference


def _get_ohio_report_card_document_token(session: requests.Session) -> str:
    page_response = session.get(OH_SOURCE_PAGE_URL, timeout=60)
    page_response.raise_for_status()

    main_bundle_match = re.search(
        r"<script[^>]+src=[\"']([^\"']*main\.[^\"']+\.js)[\"'][^>]*type=[\"']module[\"']",
        page_response.text,
        flags=re.I,
    )
    if main_bundle_match is None:
        raise RuntimeError("Could not find the Ohio School Report Cards main bundle on the download page.")

    main_bundle_url = urljoin(OH_SOURCE_PAGE_URL, main_bundle_match.group(1))
    bundle_response = session.get(main_bundle_url, timeout=60)
    bundle_response.raise_for_status()

    token_match = re.search(r'pi_documentToken="([^"]+)"', bundle_response.text)
    if token_match is None:
        raise RuntimeError("Could not find the Ohio School Report Cards document token in the main bundle.")
    return token_match.group(1)


def _build_ohio_public_reference(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[dict[str, object], dict[str, object]]:
    source_download_url = OH_SOURCE_INDEX_URL
    signed_download_url = OH_SOURCE_INDEX_URL
    cached_raw_path = repo_root / OH_RAW_RELATIVE_PATH
    if raw_workbook is None and not cached_raw_path.exists():
        index_response = session.get(OH_SOURCE_INDEX_URL, timeout=60)
        index_response.raise_for_status()
        categories = index_response.json()
        source_download_url = next(
            (
                str(item.get("fileLocation", "")).strip()
                for item in categories
                if str(item.get("title", "")).strip() == OH_SOURCE_FILE_TITLE
            ),
            "",
        )
        if not source_download_url:
            raise RuntimeError(
                "Could not find Ohio's Title 1 Proficiency by Grade 2024-2025 workbook in the official download index."
            )

        token = _get_ohio_report_card_document_token(session)
        signed_download_url = f"{source_download_url}?{token}"

    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=OH_RAW_RELATIVE_PATH,
        source_url=signed_download_url,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, sheet_name="State_Prof_by_Grade")
    row = df[
        df["State"].fillna("").astype(str).str.strip().eq("Ohio")
        & df["School Year"].fillna("").astype(str).str.strip().eq("2024-2025")
    ]
    if row.empty:
        raise RuntimeError(
            "Could not find the Ohio statewide 2024-2025 Grade 3 ELA row in the Title 1 Proficiency by Grade workbook."
        )

    record = row.iloc[0]
    proficient_or_above_pct = clean_number(record["English Language Arts 3rd Grade Percent Proficient or Above"])
    below_basic_proxy_pct = None
    if proficient_or_above_pct is not None:
        below_basic_proxy_pct = round(100.0 - proficient_or_above_pct, 2)

    source_note = (
        "Ohio School Report Cards publishes a statewide Title 1 Proficiency by Grade workbook with the Grade 3 "
        "English Language Arts Percent Proficient or Above value. The companion Title 1 Proficiency Levels workbook "
        "is statewide by student group rather than by grade, so Ohio remains an official proficiency-only source here."
    )
    summary = {
        "state": "OH",
        "state_name": "Ohio",
        "assessment": "Ohio State Tests",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "100 - Percent Proficient or Above",
        "below_basic_analog_pct": below_basic_proxy_pct,
        "official_statewide_grade3_ela_percent_proficient_or_above_pct": proficient_or_above_pct,
        "source_notes": (
            source_note
            + " The below-basic analog remains a not-proficient proxy defined here as 100 - Percent Proficient or Above."
        ),
        "source_url": source_download_url,
        "source_page_url": OH_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "OH",
        "state_name": "Ohio",
        "assessment": "Ohio State Tests",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_proficiency_only",
        "source_bin_1_label": "Percent Proficient or Above",
        "source_bin_1_pct": proficient_or_above_pct,
        "source_bin_2_label": "",
        "source_bin_2_pct": None,
        "source_bin_3_label": "",
        "source_bin_3_pct": None,
        "source_bin_4_label": "",
        "source_bin_4_pct": None,
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": source_note,
        "source_url": source_download_url,
        "source_page_url": OH_SOURCE_PAGE_URL,
    }
    _write_single_row_csv(repo_root, OH_OUTPUT_RELATIVE_PATH, published_reference)
    return summary, published_reference


def _build_maryland_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_json: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = repo_root / MD_RAW_RELATIVE_PATH
    ensure_parent(raw_path)

    if raw_json is not None:
        source = raw_json.resolve()
        if source != raw_path.resolve():
            shutil.copyfile(source, raw_path)
    elif not raw_path.exists():
        payload = {
            "SEXCODE": "3",
            "RACECODE": "6",
            "GRADE": "",
            "SWD": "3",
            "FARM": "3",
            "LEP": "3",
            "MIGRANT": "3",
            "ADA504": "3",
            "TITLE1": "3",
            "HOMELESS": "3",
            "FOSTER": "3",
            "MILITARY": "3",
            "ECODIS": "3",
            "GT": "3",
            "LEA": "99",
            "LEAID": "00",
            "SCHOOLID": "XXXX",
            "SUBJECTID": "",
            "SPECIALSERVICES": "",
            "TESTING_TYPE_ID": "1",
            "CLN_TYPE_CODE": "1",
            "GRADE_KEY": "16",
            "SUBJ_KEY": "1",
            "POVERTY_ID": "",
            "COHORT_ID": "1",
            "TypeName": "Current",
            "TREND": "",
            "EMHCode": "",
            "FILTERS": "",
            "Call": "GetELAPerformanceBarChart",
            "Value": "ELAPerformance",
            "Year": "2025",
            "PARCCAssessmentType": "",
            "MCAP2AssessmentType": "",
            "ACCT_SUM_GRP_KEY": "1",
            "SPCL_SVC_KEY": "1",
            "CR_AP_SUBJ_KEY": "88",
            "EMH_LEVEL_CODE": "",
            "LANGUAGEID": "1",
            "ResetFilters": False,
        }
        response = session.post(MD_SOURCE_DOWNLOAD_URL, json=payload, timeout=120)
        response.raise_for_status()
        write_json(raw_path, response.json())

    with raw_path.open() as infile:
        source_data = json.load(infile)

    graph_data = source_data.get("graphs", [{}])[0].get("GraphData", [])
    if not graph_data:
        raise RuntimeError("Could not find Maryland Grade 3 ELA graph data in the public MCAP response.")

    def _extract_row_value(cells: list[dict[str, object]], target_name: str) -> str:
        for cell in cells:
            if str(cell.get("Name", "")).strip() == target_name:
                return str(cell.get("Value", "")).strip()
        return ""

    def _to_percent(value: str) -> float | None:
        numeric = clean_number(value)
        if numeric is None:
            return None
        if abs(numeric) <= 1:
            return round(numeric * 100.0, 1)
        return round(numeric, 1)

    tier_lookup: dict[str, float | None] = {}
    proficient_pct: float | None = None
    for row in graph_data:
        performance_level = _extract_row_value(row, "Performance Level")
        result_pct = _to_percent(_extract_row_value(row, "Result (%)"))
        if performance_level in {"PL 1", "PL 2", "PL 3", "PL 4"}:
            tier_lookup[performance_level] = result_pct
        if performance_level == "PL 3/4":
            proficient_pct = clean_number(_extract_row_value(row, "PercProf"))
            if proficient_pct is None:
                proficient_pct = _to_percent(_extract_row_value(row, "Result (%)"))

    if set(tier_lookup) != {"PL 1", "PL 2", "PL 3", "PL 4"}:
        raise RuntimeError("Could not find all four Maryland MCAP Grade 3 ELA performance levels in the public response.")
    if proficient_pct is None:
        raise RuntimeError("Could not find Maryland's published Grade 3 ELA proficient percentage in the public response.")

    tier_specs = [
        ("pl_1", "PL 1", tier_lookup["PL 1"], True),
        ("pl_2", "PL 2", tier_lookup["PL 2"], False),
        ("pl_3", "PL 3", tier_lookup["PL 3"], False),
        ("pl_4", "PL 4", tier_lookup["PL 4"], False),
    ]
    source_note = (
        "Maryland Report Card's public 2025 MCAP English Language Arts endpoint publishes the statewide Grade 3 "
        "All Students performance-level percentages directly."
    )

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "MD",
                "state_name": "Maryland",
                "assessment": "MCAP",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "PL 1",
                "source_value_kind": "reported_exact_tier",
                "notes": source_note,
                "source_url": MD_SOURCE_DOWNLOAD_URL,
                "source_page_url": MD_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / MD_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "MD",
        "state_name": "Maryland",
        "assessment": "MCAP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "PL 1",
        "below_basic_analog_pct": tier_lookup["PL 1"],
        "official_statewide_grade3_ela_proficient_pct": proficient_pct,
        "source_notes": source_note,
        "source_url": MD_SOURCE_DOWNLOAD_URL,
        "source_page_url": MD_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "MD",
        "state_name": "Maryland",
        "assessment": "MCAP",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "PL 1",
        "source_bin_1_pct": tier_lookup["PL 1"],
        "source_bin_2_label": "PL 2",
        "source_bin_2_pct": tier_lookup["PL 2"],
        "source_bin_3_label": "PL 3",
        "source_bin_3_pct": tier_lookup["PL 3"],
        "source_bin_4_label": "PL 4",
        "source_bin_4_pct": tier_lookup["PL 4"],
        "source_bin_5_label": "PL 3/4",
        "source_bin_5_pct": proficient_pct,
        "notes": (
            "These are Maryland's published statewide 2025 Grade 3 MCAP ELA source bins, plus the combined PL 3/4 proficient share."
        ),
        "source_url": MD_SOURCE_DOWNLOAD_URL,
        "source_page_url": MD_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_massachusetts_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_html: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=MA_RAW_RELATIVE_PATH,
        source_url=MA_SOURCE_DOWNLOAD_URL,
        local_override=raw_html,
    )

    text = raw_path.read_text(encoding="utf-8", errors="ignore")
    table_match = re.search(r"<table id=['\"]tblNextGen['\"][^>]*>.*?</table>", text, flags=re.S | re.I)
    if not table_match:
        raise RuntimeError("Could not find the Massachusetts MCAS achievement-level table in the state profile HTML.")

    grade3_cells: list[str] | None = None
    for row_html in re.findall(r"<tr[^>]*>(.*?)</tr>", table_match.group(0), flags=re.S | re.I):
        cells = [_strip_html_text(cell) for cell in re.findall(r"<td[^>]*>(.*?)</td>", row_html, flags=re.S | re.I)]
        if cells and cells[0].upper() == "GRADE 03 - ENGLISH LANGUAGE ARTS":
            grade3_cells = cells
            break

    if grade3_cells is None or len(grade3_cells) < 11:
        raise RuntimeError(
            "Could not find the Massachusetts statewide Grade 3 ELA row in the MCAS achievement-level HTML."
        )

    meets_or_exceeds_pct = clean_number(grade3_cells[1])
    exceeding_pct = clean_number(grade3_cells[2])
    meeting_pct = clean_number(grade3_cells[3])
    partially_meeting_pct = clean_number(grade3_cells[4])
    not_meeting_pct = clean_number(grade3_cells[5])
    valid_test_takers = clean_number(grade3_cells[6])

    source_note = (
        "Massachusetts School and District Profiles publishes the statewide 2025 MCAS Grade 3 ELA achievement-level split "
        "directly on the state profile page, including Exceeding, Meeting, Partially Meeting, and Not Meeting Expectations."
    )

    tier_specs = [
        ("not_meeting_expectations", "Not Meeting Expectations", not_meeting_pct, True),
        ("partially_meeting_expectations", "Partially Meeting Expectations", partially_meeting_pct, False),
        ("meeting_expectations", "Meeting Expectations", meeting_pct, False),
        ("exceeding_expectations", "Exceeding Expectations", exceeding_pct, False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "MA",
                "state_name": "Massachusetts",
                "assessment": "MCAS",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Not Meeting Expectations",
                "source_value_kind": "reported_exact_tier",
                "notes": source_note,
                "source_url": MA_SOURCE_DOWNLOAD_URL,
                "source_page_url": MA_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / MA_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "MA",
        "state_name": "Massachusetts",
        "assessment": "MCAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Not Meeting Expectations",
        "below_basic_analog_pct": not_meeting_pct,
        "official_statewide_grade3_ela_met_or_exceeded_pct": meets_or_exceeds_pct,
        "official_valid_test_takers": valid_test_takers,
        "source_notes": (
            source_note
            + " The page also reports the combined Meeting or Exceeding Expectations rate directly."
        ),
        "source_url": MA_SOURCE_DOWNLOAD_URL,
        "source_page_url": MA_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "MA",
        "state_name": "Massachusetts",
        "assessment": "MCAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Not Meeting Expectations",
        "source_bin_1_pct": not_meeting_pct,
        "source_bin_2_label": "Partially Meeting Expectations",
        "source_bin_2_pct": partially_meeting_pct,
        "source_bin_3_label": "Meeting Expectations",
        "source_bin_3_pct": meeting_pct,
        "source_bin_4_label": "Exceeding Expectations",
        "source_bin_4_pct": exceeding_pct,
        "source_bin_5_label": "Meeting or Exceeding Expectations",
        "source_bin_5_pct": meets_or_exceeds_pct,
        "notes": (
            "These are Massachusetts's original published statewide Grade 3 MCAS ELA source bins, plus the page's combined "
            "Meeting or Exceeding Expectations percentage."
        ),
        "source_url": MA_SOURCE_DOWNLOAD_URL,
        "source_page_url": MA_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_north_carolina_public_bins(
    repo_root: Path,
    session: requests.Session,
    raw_workbook: Path | None,
) -> tuple[dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=NC_RAW_RELATIVE_PATH,
        source_url=NC_SOURCE_DOWNLOAD_URL,
        local_override=raw_workbook,
    )

    df = pd.read_excel(raw_path, sheet_name="Assess-Ind Data Set", dtype=str)
    row = df[
        df["lea_code"].fillna("").astype(str).str.strip().eq("NC")
        & df["school_code"].fillna("").astype(str).str.strip().eq("NC")
        & df["subgroup"].fillna("").astype(str).str.strip().eq("ALL")
        & df["subject"].fillna("").astype(str).str.strip().eq("RD03")
    ]
    if row.empty:
        raise RuntimeError("Could not find the North Carolina statewide Grade 3 reading row in the assessment workbook.")

    record = row.iloc[0]
    summary = {
        "state": "NC",
        "state_name": "North Carolina",
        "assessment": "NC EOG",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Not Proficient",
        "below_basic_analog_pct": clean_number(record["notprof_pct"]),
        "official_statewide_grade3_reading_grade_level_proficient_pct": clean_number(record["glp_pct"]),
        "source_notes": (
            "North Carolina's statewide Grade 3 reading row publishes Not Proficient plus Levels 3, 4, and 5. "
            "The Not Proficient bin aggregates Levels 1 and 2."
        ),
        "source_url": NC_SOURCE_DOWNLOAD_URL,
        "source_page_url": NC_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "NC",
        "state_name": "North Carolina",
        "assessment": "NC EOG",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_bins_levels_1_2_aggregated",
        "source_bin_1_label": "Not Proficient (Levels 1 and 2 combined)",
        "source_bin_1_pct": clean_number(record["notprof_pct"]),
        "source_bin_2_label": "Level 3",
        "source_bin_2_pct": clean_number(record["lev3_pct"]),
        "source_bin_3_label": "Level 4",
        "source_bin_3_pct": clean_number(record["lev4_pct"]),
        "source_bin_4_label": "Level 5",
        "source_bin_4_pct": clean_number(record["lev5_pct"]),
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": (
            "North Carolina's public statewide Grade 3 reading row aggregates Levels 1 and 2 into Not Proficient, "
            "so this is the closest public source-bin view available here."
        ),
        "source_url": NC_SOURCE_DOWNLOAD_URL,
        "source_page_url": NC_SOURCE_PAGE_URL,
    }
    _write_single_row_csv(repo_root, NC_OUTPUT_RELATIVE_PATH, published_reference)
    return summary, published_reference


def _build_pennsylvania_tiers(
    repo_root: Path,
    session: requests.Session,
    raw_html: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=PA_RAW_RELATIVE_PATH,
        source_url=PA_SOURCE_DOWNLOAD_URL,
        local_override=raw_html,
    )

    html_text = raw_path.read_text(encoding="utf-8", errors="ignore")
    section_match = re.search(
        r"<h3>\s*2025 PSSA English Language Arts Results\s*</h3>\s*<table[^>]*>\s*<tbody>(.*?)</tbody>\s*</table>",
        html_text,
        flags=re.S,
    )
    if section_match is None:
        raise RuntimeError("Could not find the Pennsylvania statewide PSSA ELA table in the reporting page.")

    row_matches = re.findall(r"<tr>(.*?)</tr>", section_match.group(1), flags=re.S)
    record_cells: list[str] | None = None
    for row_html in row_matches:
        cells = [_strip_html_text(cell) for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, flags=re.S)]
        if len(cells) != 8:
            continue
        if cells[0].lower() == "english language arts" and cells[1] == "3":
            record_cells = cells
            break

    if record_cells is None:
        raise RuntimeError("Could not find the Pennsylvania statewide Grade 3 PSSA ELA row in the reporting page.")

    record = {
        "subject": record_cells[0],
        "grade": record_cells[1],
        "number_scored": record_cells[2],
        "percent_advanced": record_cells[3],
        "percent_proficient": record_cells[4],
        "percent_basic": record_cells[5],
        "percent_below_basic": record_cells[6],
        "percent_proficient_and_above": record_cells[7],
    }
    source_note = (
        "Pennsylvania's official assessment reporting page publishes statewide Grade 3 PSSA ELA percentages for "
        "Advanced, Proficient, Basic, and Below Basic directly in the public HTML table."
    )
    tier_specs = [
        ("below_basic", "Below Basic", record["percent_below_basic"], True),
        ("basic", "Basic", record["percent_basic"], False),
        ("proficient", "Proficient", record["percent_proficient"], False),
        ("advanced", "Advanced", record["percent_advanced"], False),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "PA",
                "state_name": "Pennsylvania",
                "assessment": "PSSA",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": clean_number(value),
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Below Basic",
                "source_value_kind": "reported_exact_tier",
                "notes": source_note,
                "source_url": PA_SOURCE_DOWNLOAD_URL,
                "source_page_url": PA_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / PA_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "PA",
        "state_name": "Pennsylvania",
        "assessment": "PSSA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Below Basic",
        "below_basic_analog_pct": clean_number(record["percent_below_basic"]),
        "official_statewide_grade3_ela_proficient_or_advanced_pct": clean_number(record["percent_proficient_and_above"]),
        "official_number_scored": clean_number(record["number_scored"]),
        "source_notes": source_note,
        "source_url": PA_SOURCE_DOWNLOAD_URL,
        "source_page_url": PA_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "PA",
        "state_name": "Pennsylvania",
        "assessment": "PSSA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Below Basic",
        "source_bin_1_pct": clean_number(record["percent_below_basic"]),
        "source_bin_2_label": "Basic",
        "source_bin_2_pct": clean_number(record["percent_basic"]),
        "source_bin_3_label": "Proficient",
        "source_bin_3_pct": clean_number(record["percent_proficient"]),
        "source_bin_4_label": "Advanced",
        "source_bin_4_pct": clean_number(record["percent_advanced"]),
        "source_bin_5_label": "Proficient and above",
        "source_bin_5_pct": clean_number(record["percent_proficient_and_above"]),
        "notes": (
            "Pennsylvania's public assessment reporting page publishes the statewide Grade 3 PSSA ELA row directly, "
            "including the four achievement levels and the combined Proficient and above rate."
        ),
        "source_url": PA_SOURCE_DOWNLOAD_URL,
        "source_page_url": PA_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_rhode_island_tiers(
    repo_root: Path,
    raw_json: Path | None,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    raw_path = repo_root / RI_RAW_RELATIVE_PATH
    ensure_parent(raw_path)

    if raw_json is not None:
        source = raw_json.resolve()
        if source != raw_path.resolve():
            shutil.copyfile(source, raw_path)
    elif not raw_path.exists():
        raise RuntimeError(
            "Rhode Island raw extract is missing. Save the public ADP Grade 3 ELA report extract to "
            f"{raw_path} or pass --ri-raw-json."
        )

    with raw_path.open() as infile:
        source_data = json.load(infile)

    level_lookup = {
        str(entry["label"]).strip(): entry for entry in source_data.get("performance_levels", [])
    }
    expected_levels = [
        "Not Meeting Expectations",
        "Partially Meeting Expectations",
        "Meeting Expectations",
        "Exceeding Expectations",
    ]
    missing_levels = [level for level in expected_levels if level not in level_lookup]
    if missing_levels:
        raise RuntimeError(
            "Rhode Island saved extract is missing Grade 3 ELA performance levels: "
            + ", ".join(missing_levels)
        )

    students_tested = clean_number(source_data.get("students_tested"))
    participation_rate = clean_number(source_data.get("participation_rate"))
    average_scale_score = clean_number(source_data.get("average_scale_score"))
    meeting_or_exceeding_pct = clean_number(source_data.get("meeting_or_exceeding_expectations_pct"))
    source_note = (
        "Rhode Island's public Assessment Data Portal publishes statewide Grade 3 RICAS ELA performance-level "
        "percentages directly for All Students."
    )
    tier_specs = [
        (
            "not_meeting_expectations",
            "Not Meeting Expectations",
            clean_number(level_lookup["Not Meeting Expectations"].get("pct")),
            True,
        ),
        (
            "partially_meeting_expectations",
            "Partially Meeting Expectations",
            clean_number(level_lookup["Partially Meeting Expectations"].get("pct")),
            False,
        ),
        (
            "meeting_expectations",
            "Meeting Expectations",
            clean_number(level_lookup["Meeting Expectations"].get("pct")),
            False,
        ),
        (
            "exceeding_expectations",
            "Exceeding Expectations",
            clean_number(level_lookup["Exceeding Expectations"].get("pct")),
            False,
        ),
    ]

    rows: list[dict[str, object]] = []
    for tier_rank, (tier_id, tier_label, value, is_below_basic) in enumerate(tier_specs, start=1):
        rows.append(
            {
                "state": "RI",
                "state_name": "Rhode Island",
                "assessment": "RICAS",
                "subject": "ELA",
                "subject_label": "English Language Arts",
                "grade": "03",
                "school_year": "2024-2025",
                "administration_year": 2025,
                "tier_rank": tier_rank,
                "tier_id": tier_id,
                "tier_label": tier_label,
                "pct_students": value,
                "is_below_basic_analog": is_below_basic,
                "below_basic_analog_label": "Not Meeting Expectations",
                "source_value_kind": "reported_exact_tier",
                "notes": source_note,
                "source_url": RI_SOURCE_DOWNLOAD_URL,
                "source_page_url": RI_SOURCE_PAGE_URL,
            }
        )

    tiers_df = pd.DataFrame(rows)
    output_path = repo_root / RI_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    tiers_df.to_csv(output_path, index=False)

    summary = {
        "state": "RI",
        "state_name": "Rhode Island",
        "assessment": "RICAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Not Meeting Expectations",
        "below_basic_analog_pct": clean_number(level_lookup["Not Meeting Expectations"].get("pct")),
        "official_statewide_grade3_ela_met_or_exceeded_pct": meeting_or_exceeding_pct,
        "official_valid_test_takers": students_tested,
        "official_statewide_grade3_ela_participation_rate": participation_rate,
        "source_notes": (
            source_note
            + f" The saved extract also reports {students_tested} students tested and an average scale score of "
            f"{average_scale_score}."
        ),
        "source_url": RI_SOURCE_DOWNLOAD_URL,
        "source_page_url": RI_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "RI",
        "state_name": "Rhode Island",
        "assessment": "RICAS",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_exact_tiers",
        "source_bin_1_label": "Not Meeting Expectations",
        "source_bin_1_pct": clean_number(level_lookup["Not Meeting Expectations"].get("pct")),
        "source_bin_2_label": "Partially Meeting Expectations",
        "source_bin_2_pct": clean_number(level_lookup["Partially Meeting Expectations"].get("pct")),
        "source_bin_3_label": "Meeting Expectations",
        "source_bin_3_pct": clean_number(level_lookup["Meeting Expectations"].get("pct")),
        "source_bin_4_label": "Exceeding Expectations",
        "source_bin_4_pct": clean_number(level_lookup["Exceeding Expectations"].get("pct")),
        "source_bin_5_label": "Meeting or Exceeding Expectations",
        "source_bin_5_pct": meeting_or_exceeding_pct,
        "notes": (
            "These are Rhode Island's published statewide 2024-25 Grade 3 RICAS ELA source bins, plus the portal's "
            "combined Meeting or Exceeding Expectations percentage."
        ),
        "source_url": RI_SOURCE_DOWNLOAD_URL,
        "source_page_url": RI_SOURCE_PAGE_URL,
    }
    return tiers_df, summary, published_reference


def _build_virginia_public_bins(
    repo_root: Path,
    session: requests.Session,
    raw_html: Path | None,
) -> tuple[dict[str, object], dict[str, object]]:
    raw_path = _copy_or_download_file(
        repo_root=repo_root,
        session=session,
        destination_relative_path=VA_RAW_RELATIVE_PATH,
        source_url=VA_SOURCE_DOWNLOAD_URL,
        local_override=raw_html,
    )

    html_text = raw_path.read_text(encoding="utf-8", errors="ignore")
    table_match = re.search(r"<tbody class='table-data-Reading-1'>(.*?)</tbody>", html_text, flags=re.S)
    if table_match is None:
        raise RuntimeError("Could not find the Virginia Grade 3 English Reading statewide table in the state profile page.")

    all_students_match = re.search(r"<tr>\s*<th>All Students</th>(.*?)</tr>", table_match.group(1), flags=re.S)
    if all_students_match is None:
        raise RuntimeError("Could not find the Virginia All Students row in the Grade 3 English Reading table.")

    cells = [_strip_html_text(cell) for cell in re.findall(r"<td>(.*?)</td>", all_students_match.group(1), flags=re.S)]
    if len(cells) < 12:
        raise RuntimeError(
            f"Expected 12 Virginia Grade 3 English Reading statewide cells, found {len(cells)}."
        )

    school_years = ["2022-2023", "2023-2024", "2024-2025"]
    by_year: dict[str, dict[str, float | None]] = {}
    for year_index, school_year in enumerate(school_years):
        offset = year_index * 4
        by_year[school_year] = {
            "advanced": clean_number(cells[offset]),
            "proficient": clean_number(cells[offset + 1]),
            "passed": clean_number(cells[offset + 2]),
            "failed": clean_number(cells[offset + 3]),
        }

    latest = by_year["2024-2025"]
    summary = {
        "state": "VA",
        "state_name": "Virginia",
        "assessment": "SOL",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "below_basic_analog_label": "Failed",
        "below_basic_analog_pct": latest["failed"],
        "official_statewide_grade3_reading_advanced_pct": latest["advanced"],
        "official_statewide_grade3_reading_proficient_pct": latest["proficient"],
        "official_statewide_grade3_reading_passed_pct": latest["passed"],
        "source_notes": (
            "Virginia School Quality Profiles publishes statewide Grade 3 English Reading percentages for Advanced, "
            "Proficient, Passed, and Failed. Failed is used here as the below-basic analog because the public source "
            "does not split non-passing students into finer statewide tiers."
        ),
        "source_url": VA_SOURCE_DOWNLOAD_URL,
        "source_page_url": VA_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "VA",
        "state_name": "Virginia",
        "assessment": "SOL",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2024-2025",
        "administration_year": 2025,
        "source_bin_structure": "published_pass_rate_breakout",
        "source_bin_1_label": "Advanced",
        "source_bin_1_pct": latest["advanced"],
        "source_bin_2_label": "Proficient",
        "source_bin_2_pct": latest["proficient"],
        "source_bin_3_label": "Passed",
        "source_bin_3_pct": latest["passed"],
        "source_bin_4_label": "Failed",
        "source_bin_4_pct": latest["failed"],
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": (
            "Virginia's public state profile publishes the statewide Grade 3 English Reading row with Advanced, "
            "Proficient, Passed, and Failed columns."
        ),
        "source_url": VA_SOURCE_DOWNLOAD_URL,
        "source_page_url": VA_SOURCE_PAGE_URL,
    }
    _write_single_row_csv(repo_root, VA_OUTPUT_RELATIVE_PATH, published_reference)
    return summary, published_reference


def _build_west_virginia_public_reference(repo_root: Path) -> tuple[dict[str, object], dict[str, object]]:
    summary = {
        "state": "WV",
        "state_name": "West Virginia",
        "assessment": "WVGSA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2023-2024",
        "administration_year": 2024,
        "below_basic_analog_label": "100 - Meets Standard or above",
        "below_basic_analog_pct": 49.0,
        "official_statewide_grade3_ela_meets_standard_or_above_pct": 51.0,
        "source_notes": (
            "West Virginia's public statewide Grade 3 ELA materials expose proficiency but not the full statewide "
            "performance-level split, so the below-basic analog is filled as 100 - Meets Standard or above."
        ),
        "source_url": WV_SOURCE_DOWNLOAD_URL,
        "source_page_url": WV_SOURCE_PAGE_URL,
    }
    published_reference = {
        "state": "WV",
        "state_name": "West Virginia",
        "assessment": "WVGSA",
        "subject": "ELA",
        "grade": "03",
        "school_year": "2023-2024",
        "administration_year": 2024,
        "source_bin_structure": "published_proficiency_only",
        "source_bin_1_label": "Meets Standard or above (proficient)",
        "source_bin_1_pct": 51.0,
        "source_bin_2_label": "",
        "source_bin_2_pct": None,
        "source_bin_3_label": "",
        "source_bin_3_pct": None,
        "source_bin_4_label": "",
        "source_bin_4_pct": None,
        "source_bin_5_label": "",
        "source_bin_5_pct": None,
        "notes": (
            "The public WVDE 2024 assessment PDF reports statewide Grade 3 ELA proficiency at 51%. "
            "The public sources used here did not expose the full statewide split across Does Not Meet, "
            "Partially Meets, Meets, and Exceeds without an authenticated dashboard session."
        ),
        "source_url": WV_SOURCE_DOWNLOAD_URL,
        "source_page_url": WV_SOURCE_PAGE_URL,
    }

    output_path = repo_root / WV_REFERENCE_OUTPUT_RELATIVE_PATH
    ensure_parent(output_path)
    pd.DataFrame([published_reference]).to_csv(output_path, index=False)
    return summary, published_reference


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
    combined = combined[
        combined["path"].ne("datasets/ma/mcas/2024_2025/processed/mcas_2025_statewide_grade3_ela_public_reference.csv")
    ]
    combined = combined.sort_values(by=["state", "program", "reporting_period", "kind", "path"], kind="stable")
    ensure_parent(catalog_path)
    combined.to_csv(catalog_path, index=False)


def _write_rollout_tracker(
    repo_root: Path,
    below_basic_df: pd.DataFrame,
    published_reference_df: pd.DataFrame,
    proxy_df: pd.DataFrame,
) -> Path:
    below_basic_by_state = {
        str(row["state"]): row
        for _, row in below_basic_df.sort_values(
            by=["state", "administration_year"], ascending=[True, False], kind="stable"
        ).iterrows()
    }
    published_reference_by_state = {
        str(row["state"]): row
        for _, row in published_reference_df.sort_values(
            by=["state", "administration_year"], ascending=[True, False], kind="stable"
        ).iterrows()
    }
    proxy_by_state = {
        str(row["state"]): row
        for _, row in proxy_df.sort_values(
            by=["state", "administration_year"], ascending=[True, False], kind="stable"
        ).iterrows()
    }

    rows = []
    for state_code, state_name in STATE_INFO:
        if state_code in EXACT_TIER_STATES:
            row = below_basic_by_state[state_code]
            rows.append(
                (
                    state_code,
                    state_name,
                    "covered_exact_tiers",
                    str(row["assessment"]),
                    str(row["school_year"]),
                    str(row["source_notes"]),
                    str(row["source_page_url"]),
                )
            )
            continue

        if state_code in SOURCE_BIN_STATES:
            row = below_basic_by_state[state_code]
            rows.append(
                (
                    state_code,
                    state_name,
                    "covered_source_bins",
                    str(row["assessment"]),
                    str(row["school_year"]),
                    str(row["source_notes"]),
                    str(row["source_page_url"]),
                )
            )
            continue

        if state_code in OFFICIAL_PROFICIENCY_ONLY_STATES and state_code in below_basic_by_state:
            row = below_basic_by_state[state_code]
            rows.append(
                (
                    state_code,
                    state_name,
                    "covered_official_proficiency_proxy",
                    str(row["assessment"]),
                    str(row["school_year"]),
                    str(row["source_notes"]),
                    str(row["source_page_url"]),
                )
            )
            continue

        if state_code in proxy_by_state:
            row = proxy_by_state[state_code]
            note = str(row["source_notes"])
            if state_code in {"DE", "MA", "WV"}:
                note += " A more recent state-specific proficiency-only reference is also retained in the published reference file."
            rows.append(
                (
                    state_code,
                    state_name,
                    "covered_federal_proficiency_proxy",
                    str(row["assessment"]),
                    str(row["school_year"]),
                    note,
                    str(row["source_page_url"]),
                )
            )
            continue

        if state_code in published_reference_by_state:
            row = published_reference_by_state[state_code]
            rows.append(
                (
                    state_code,
                    state_name,
                    "covered_reference_only",
                    str(row["assessment"]),
                    str(row["school_year"]),
                    str(row["notes"]),
                    str(row["source_page_url"]),
                )
            )
            continue

        if state_code == "VA":
            rows.append(
                (
                    "VA",
                    "Virginia",
                    "missing_public_proxy",
                    "Statewide RLA Assessment (Ed Data Express)",
                    "",
                    "No public Ed Data Express statewide Grade 3 reading row was available for Virginia under the 2021-2022 or 2020-2021 SEA filter, so the below-basic analog remains unfilled.",
                    ED_DATA_EXPRESS_SOURCE_PAGE_URL,
                )
            )
            continue

        rows.append((state_code, state_name, "not_started", "", "", "", ""))
    tracker_df = pd.DataFrame(
        rows,
        columns=[
            "state",
            "state_name",
            "status",
            "assessment",
            "school_year",
            "notes",
            "source_page_url",
        ],
    )
    output_path = repo_root / ROLLOUT_TRACKER_RELATIVE_PATH
    ensure_parent(output_path)
    tracker_df.to_csv(output_path, index=False)
    return output_path


def build_statewide_grade3_ela(
    repo_root: Path,
    session: requests.Session,
    ak_raw_pdf: Path | None = None,
    ar_raw_workbook: Path | None = None,
    ca_raw_workbook: Path | None = None,
    co_raw_workbook: Path | None = None,
    ct_raw_json: Path | None = None,
    dc_raw_workbook: Path | None = None,
    fl_raw_workbook: Path | None = None,
    ga_raw_workbook: Path | None = None,
    in_raw_workbook: Path | None = None,
    la_raw_workbook: Path | None = None,
    ma_raw_html: Path | None = None,
    md_raw_json: Path | None = None,
    nc_raw_workbook: Path | None = None,
    nj_raw_workbook: Path | None = None,
    oh_raw_workbook: Path | None = None,
    pa_raw_html: Path | None = None,
    ri_raw_json: Path | None = None,
    tn_raw_workbook: Path | None = None,
    tx_raw_workbook: Path | None = None,
    va_raw_html: Path | None = None,
    wa_raw_csv: Path | None = None,
    wi_raw_zip: Path | None = None,
) -> dict[str, Path]:
    alaska_tiers, alaska_summary, alaska_published_reference = _build_alaska_tiers(
        repo_root,
        session,
        ak_raw_pdf,
    )
    arkansas_tiers, arkansas_summary, arkansas_published_reference = _build_arkansas_tiers(
        repo_root,
        session,
        ar_raw_workbook,
    )
    california_summary, california_published_reference = _build_california_public_reference(
        repo_root,
        session,
        ca_raw_workbook,
    )
    colorado_tiers, colorado_summary, colorado_published_reference = _build_colorado_tiers(
        repo_root,
        session,
        co_raw_workbook,
    )
    connecticut_tiers, connecticut_summary, connecticut_published_reference = _build_connecticut_tiers(
        repo_root,
        ct_raw_json,
    )
    dc_tiers, dc_summary, dc_published_reference = _build_dc_tiers(
        repo_root,
        session,
        dc_raw_workbook,
    )
    florida_tiers, florida_summary, florida_published_reference = _build_florida_tiers(
        repo_root,
        session,
        fl_raw_workbook,
    )
    georgia_tiers, georgia_summary, georgia_published_reference = _build_georgia_tiers(
        repo_root,
        session,
        ga_raw_workbook,
    )
    indiana_tiers, indiana_summary, indiana_published_reference = _build_indiana_tiers(
        repo_root,
        session,
        in_raw_workbook,
    )
    kentucky_tiers, kentucky_summary, kentucky_published_reference = _build_kentucky_tiers(repo_root)
    louisiana_tiers, louisiana_summary, louisiana_published_reference = _build_louisiana_tiers(
        repo_root,
        session,
        la_raw_workbook,
    )
    maryland_tiers, maryland_summary, maryland_published_reference = _build_maryland_tiers(
        repo_root,
        session,
        md_raw_json,
    )
    massachusetts_tiers, massachusetts_summary, massachusetts_published_reference = _build_massachusetts_tiers(
        repo_root,
        session,
        ma_raw_html,
    )
    mississippi_tiers, mississippi_summary, mississippi_published_reference = _build_mississippi_tiers(repo_root)
    new_jersey_tiers, new_jersey_summary, new_jersey_published_reference = _build_new_jersey_tiers(
        repo_root,
        session,
        nj_raw_workbook,
    )
    new_york_tiers, new_york_summary, new_york_published_reference = _build_new_york_tiers(repo_root)
    north_carolina_summary, north_carolina_published_reference = _build_north_carolina_public_bins(
        repo_root,
        session,
        nc_raw_workbook,
    )
    ohio_summary, ohio_published_reference = _build_ohio_public_reference(
        repo_root,
        session,
        oh_raw_workbook,
    )
    pennsylvania_tiers, pennsylvania_summary, pennsylvania_published_reference = _build_pennsylvania_tiers(
        repo_root,
        session,
        pa_raw_html,
    )
    rhode_island_tiers, rhode_island_summary, rhode_island_published_reference = _build_rhode_island_tiers(
        repo_root,
        ri_raw_json,
    )
    virginia_summary, virginia_published_reference = _build_virginia_public_bins(
        repo_root,
        session,
        va_raw_html,
    )
    south_carolina_tiers, south_carolina_summary, south_carolina_published_reference = _build_south_carolina_tiers(repo_root)
    tennessee_tiers, tennessee_summary, tennessee_published_reference = _build_tennessee_tiers(
        repo_root,
        session,
        tn_raw_workbook,
    )
    texas_tiers, texas_summary, texas_published_reference = _build_texas_tiers(
        repo_root,
        session,
        tx_raw_workbook,
    )
    washington_tiers, washington_summary, washington_published_reference = _build_washington_tiers(
        repo_root,
        session,
        wa_raw_csv,
    )
    wisconsin_tiers, wisconsin_summary, wisconsin_published_reference = _build_wisconsin_tiers(
        repo_root,
        session,
        wi_raw_zip,
    )
    delaware_summary, delaware_published_reference = _build_delaware_public_reference(repo_root)
    new_hampshire_summary, new_hampshire_published_reference = _build_new_hampshire_public_reference(repo_root)
    west_virginia_summary, west_virginia_published_reference = _build_west_virginia_public_reference(repo_root)
    (
        official_state_tiers,
        official_state_summaries,
        official_state_references,
        official_state_outputs,
        official_state_catalog_entries,
    ) = _build_official_state_records(repo_root)
    ed_data_express_proxy_df, ed_data_express_proxy_summaries, ed_data_express_proxy_references = (
        _build_ed_data_express_proxy_rows(repo_root)
    )

    summary_df = pd.concat(
        [
            alaska_tiers,
            arkansas_tiers,
            colorado_tiers,
            connecticut_tiers,
            dc_tiers,
            florida_tiers,
            georgia_tiers,
            indiana_tiers,
            kentucky_tiers,
            louisiana_tiers,
            maryland_tiers,
            massachusetts_tiers,
            mississippi_tiers,
            new_jersey_tiers,
            new_york_tiers,
            pennsylvania_tiers,
            rhode_island_tiers,
            south_carolina_tiers,
            tennessee_tiers,
            texas_tiers,
            washington_tiers,
            wisconsin_tiers,
            official_state_tiers,
        ],
        ignore_index=True,
    ).sort_values(by=["state", "tier_rank"], kind="stable")
    summary_output_path = repo_root / SUMMARY_RELATIVE_PATH
    ensure_parent(summary_output_path)
    summary_df.to_csv(summary_output_path, index=False)

    below_basic_rows = [
        alaska_summary,
        arkansas_summary,
        california_summary,
        colorado_summary,
        connecticut_summary,
        dc_summary,
        delaware_summary,
        florida_summary,
        georgia_summary,
        indiana_summary,
        kentucky_summary,
        louisiana_summary,
        maryland_summary,
        massachusetts_summary,
        mississippi_summary,
        new_jersey_summary,
        new_york_summary,
        new_hampshire_summary,
        north_carolina_summary,
        ohio_summary,
        pennsylvania_summary,
        rhode_island_summary,
        south_carolina_summary,
        tennessee_summary,
        texas_summary,
        virginia_summary,
        washington_summary,
        west_virginia_summary,
        wisconsin_summary,
    ]
    below_basic_rows.extend(official_state_summaries)
    existing_below_basic_states = {str(row["state"]) for row in below_basic_rows}
    proxy_states_added = {
        str(row["state"])
        for row in ed_data_express_proxy_summaries
        if str(row["state"]) not in existing_below_basic_states
    }
    below_basic_rows.extend(
        row for row in ed_data_express_proxy_summaries if str(row["state"]) in proxy_states_added
    )
    below_basic_df = pd.DataFrame(below_basic_rows).sort_values(by=["state"], kind="stable")
    still_missing_after_proxy_check = sorted(
        state_code for state_code, _ in STATE_INFO if state_code not in set(below_basic_df["state"].astype(str))
    )
    below_basic_output_path = repo_root / BELOW_BASIC_RELATIVE_PATH
    ensure_parent(below_basic_output_path)
    below_basic_df.to_csv(below_basic_output_path, index=False)

    published_reference_rows = [
        alaska_published_reference,
        arkansas_published_reference,
        california_published_reference,
        colorado_published_reference,
        connecticut_published_reference,
        dc_published_reference,
        delaware_published_reference,
        florida_published_reference,
        georgia_published_reference,
        indiana_published_reference,
        kentucky_published_reference,
        louisiana_published_reference,
        maryland_published_reference,
        massachusetts_published_reference,
        mississippi_published_reference,
        new_jersey_published_reference,
        new_york_published_reference,
        new_hampshire_published_reference,
        north_carolina_published_reference,
        ohio_published_reference,
        pennsylvania_published_reference,
        rhode_island_published_reference,
        south_carolina_published_reference,
        tennessee_published_reference,
        texas_published_reference,
        virginia_published_reference,
        washington_published_reference,
        west_virginia_published_reference,
        wisconsin_published_reference,
    ]
    published_reference_rows.extend(official_state_references)
    published_reference_rows.extend(
        row for row in ed_data_express_proxy_references if str(row["state"]) in proxy_states_added
    )
    published_reference_df = pd.DataFrame(published_reference_rows).sort_values(by=["state"], kind="stable")
    published_reference_output_path = repo_root / PUBLISHED_REFERENCE_RELATIVE_PATH
    ensure_parent(published_reference_output_path)
    published_reference_df.to_csv(published_reference_output_path, index=False)

    metadata = {
        "build_date": dt.date.today().isoformat(),
        "description": "Cross-state Grade 3 ELA performance tiers and statewide source-bin references with a derived below-basic analog.",
        "outputs": {
            "alaska_statewide_tiers_csv": str(AK_OUTPUT_RELATIVE_PATH),
            "arkansas_statewide_tiers_csv": str(AR_OUTPUT_RELATIVE_PATH),
            "california_public_reference_csv": str(CA_OUTPUT_RELATIVE_PATH),
            "cross_state_below_basic_analog_csv": str(BELOW_BASIC_RELATIVE_PATH),
            "cross_state_published_reference_bins_csv": str(PUBLISHED_REFERENCE_RELATIVE_PATH),
            "cross_state_tiers_csv": str(SUMMARY_RELATIVE_PATH),
            "colorado_statewide_tiers_csv": str(CO_OUTPUT_RELATIVE_PATH),
            "connecticut_statewide_tiers_csv": str(CT_OUTPUT_RELATIVE_PATH),
            "dc_cape_statewide_tiers_csv": str(DC_OUTPUT_RELATIVE_PATH),
            "delaware_public_reference_csv": str(DE_OUTPUT_RELATIVE_PATH),
            "ed_data_express_proxy_source_csv": str(ED_DATA_EXPRESS_PROXY_RELATIVE_PATH),
            "florida_statewide_tiers_csv": str(FL_OUTPUT_RELATIVE_PATH),
            "georgia_statewide_tiers_csv": str(GA_OUTPUT_RELATIVE_PATH),
            "indiana_statewide_tiers_csv": str(IN_OUTPUT_RELATIVE_PATH),
            "kentucky_statewide_tiers_csv": str(KY_OUTPUT_RELATIVE_PATH),
            "louisiana_statewide_tiers_csv": str(LA_OUTPUT_RELATIVE_PATH),
            "maryland_statewide_tiers_csv": str(MD_OUTPUT_RELATIVE_PATH),
            "massachusetts_statewide_tiers_csv": str(MA_OUTPUT_RELATIVE_PATH),
            "mississippi_statewide_tiers_csv": str(MS_OUTPUT_RELATIVE_PATH),
            "new_jersey_statewide_tiers_csv": str(NJ_OUTPUT_RELATIVE_PATH),
            "new_york_statewide_tiers_csv": str(NY_OUTPUT_RELATIVE_PATH),
            "new_hampshire_public_reference_csv": str(NH_OUTPUT_RELATIVE_PATH),
            "north_carolina_public_bins_csv": str(NC_OUTPUT_RELATIVE_PATH),
            "ohio_public_reference_csv": str(OH_OUTPUT_RELATIVE_PATH),
            "pennsylvania_statewide_tiers_csv": str(PA_OUTPUT_RELATIVE_PATH),
            "rhode_island_statewide_tiers_csv": str(RI_OUTPUT_RELATIVE_PATH),
            "rollout_tracker_csv": str(ROLLOUT_TRACKER_RELATIVE_PATH),
            "south_carolina_statewide_tiers_csv": str(SC_OUTPUT_RELATIVE_PATH),
            "tennessee_statewide_tiers_csv": str(TN_OUTPUT_RELATIVE_PATH),
            "texas_statewide_tiers_csv": str(TX_OUTPUT_RELATIVE_PATH),
            "texas_field_guide_csv": str(TX_FIELD_GUIDE_RELATIVE_PATH),
            "virginia_public_bins_csv": str(VA_OUTPUT_RELATIVE_PATH),
            "washington_statewide_tiers_csv": str(WA_OUTPUT_RELATIVE_PATH),
            "west_virginia_public_reference_csv": str(WV_REFERENCE_OUTPUT_RELATIVE_PATH),
            "wisconsin_statewide_tiers_csv": str(WI_OUTPUT_RELATIVE_PATH),
        },
        "state_logic": {
            "AK": {
                "below_basic_analog": "Needs Support",
                "tier_logic": (
                    "Use Alaska's published statewide Grade 3 AK STAR ELA performance-level percentages from the 2025 "
                    "assessment brief, cross-checked against the statewide results page's Advanced / Proficient rate."
                ),
            },
            "AR": {
                "below_basic_analog": "Level 1",
                "tier_logic": "Use Arkansas's reported exact statewide Grade 3 ATLAS ELA performance-level percentages.",
            },
            "CA": {
                "below_basic_analog": "100 - Standard Met/Exceeded",
                "tier_logic": (
                    "Use California's 2025 CAASPP Grade 3 ELA statewide workbook as an official proficiency-only source. "
                    "The below-basic analog remains 100 - Standard Met/Exceeded because the public workbook used here "
                    "does not expose the full statewide performance-level split."
                ),
            },
            "CO": {
                "below_basic_analog": "Did Not Yet Meet Expectations",
                "tier_logic": "Use Colorado's reported exact statewide CMAS performance-level percentages.",
            },
            "CT": {
                "below_basic_analog": "Level 1 Not Met",
                "tier_logic": (
                    "Use Connecticut EdSight's public 2024-25 Smarter Balanced Grade 3 ELA report, which publishes "
                    "the statewide All Students percentages for Levels 1 through 4 plus the combined Level 3&4 rate."
                ),
            },
            "DC": {
                "below_basic_analog": "Did Not Yet Meet Expectations",
                "tier_logic": (
                    "Use OSSE's published statewide Grade 3 DC CAPE ELA Performance Level sheet, which reports "
                    "exact Levels 1 through 5 for DC CAPE separately from MSAA."
                ),
            },
            "DE": {
                "below_basic_analog": "100 - Met Achievement Standard",
                "tier_logic": (
                    "Use Delaware's public statewide Grade 3 ELA proficiency figure as an official proficiency-only "
                    "proxy. The public rows used here do not expose the full statewide performance-level split."
                ),
            },
            "FL": {
                "below_basic_analog": "Level 1",
                "tier_logic": "Use Florida's reported exact statewide Grade 3 FAST ELA PM3 percentages for Levels 1 through 5.",
            },
            "GA": {
                "below_basic_analog": "Beginning Learner",
                "tier_logic": "Use Georgia's reported exact statewide Grade 3 Georgia Milestones ELA performance-level percentages.",
            },
            "IN": {
                "below_basic_analog": "Below Proficiency",
                "tier_logic": "Use Indiana's published statewide Grade 3 ILEARN counts by tier and derive percentages from counts / total tested.",
            },
            "KY": {
                "below_basic_analog": "Novice",
                "tier_logic": "Use Kentucky's reported exact statewide Grade 3 Reading performance-level percentages from the KSA yearbook.",
            },
            "LA": {
                "below_basic_analog": "Unsatisfactory",
                "tier_logic": "Use Louisiana's reported exact statewide Grade 3 LEAP ELA achievement-level percentages from the State LEA achievement summary workbook.",
            },
            "MD": {
                "below_basic_analog": "PL 1",
                "tier_logic": (
                    "Use Maryland Report Card's public 2025 MCAP Grade 3 English Language Arts endpoint, which "
                    "reports statewide All Students percentages for PL 1 through PL 4 plus the combined PL 3/4 proficient share."
                ),
            },
            "MA": {
                "below_basic_analog": "Not Meeting Expectations",
                "tier_logic": (
                    "Use Massachusetts's statewide 2025 MCAS Grade 3 ELA achievement-level page, which reports "
                    "Exceeding, Meeting, Partially Meeting, and Not Meeting Expectations directly."
                ),
            },
            "MS": {
                "below_basic_analog": "Minimal",
                "tier_logic": "Use Mississippi's reported exact statewide Grade 3 MAAP ELA performance-level percentages from the 2025 executive summary PDF.",
            },
            "NC": {
                "below_basic_analog": "Not Proficient",
                "tier_logic": "Use North Carolina's public statewide Grade 3 reading bins, where Not Proficient aggregates Levels 1 and 2 and Levels 3 through 5 are published separately.",
            },
            "NH": {
                "below_basic_analog": "100 - Percent Proficient",
                "tier_logic": (
                    "Use New Hampshire's official iPlatform 2025 Grade 3 NH SAS ELA proficiency rate as an official "
                    "proficiency-only source. The below-basic analog remains 100 - Percent Proficient because the "
                    "public result used here does not expose the full statewide performance-level split."
                ),
            },
            "OH": {
                "below_basic_analog": "100 - Percent Proficient or Above",
                "tier_logic": (
                    "Use Ohio School Report Cards' 2024-2025 Title 1 Proficiency by Grade workbook as an official "
                    "proficiency-only source. The public Grade 3 ELA row reports Percent Proficient or Above, while "
                    "the companion Title 1 Proficiency Levels workbook is not broken out by grade."
                ),
            },
            "NJ": {
                "below_basic_analog": "Level 1",
                "tier_logic": "Use New Jersey's reported exact statewide Grade 3 NJSLA ELA performance-level percentages.",
            },
            "NY": {
                "below_basic_analog": "Level 1",
                "tier_logic": (
                    "Use the NYSED Data Site 2024-25 Report Card Database Annual EM ELA table, which reports "
                    "All Public Schools statewide Grade 3 ELA counts and tested percentages for Levels 1 through 4."
                ),
            },
            "PA": {
                "below_basic_analog": "Below Basic",
                "tier_logic": "Use Pennsylvania's reported exact statewide Grade 3 PSSA ELA performance-level percentages.",
            },
            "RI": {
                "below_basic_analog": "Not Meeting Expectations",
                "tier_logic": (
                    "Use Rhode Island's public Assessment Data Portal 2024-25 Grade 3 RICAS ELA statewide report, "
                    "which publishes All Students percentages for the four performance levels plus Meeting or Exceeding Expectations."
                ),
            },
            "SC": {
                "below_basic_analog": "Does Not Meet Expectations",
                "tier_logic": "Use South Carolina's reported exact statewide Grade 3 SC READY ELA performance-level percentages from the public state results page.",
            },
            "TN": {
                "below_basic_analog": "Below",
                "tier_logic": "Use Tennessee's reported exact statewide Grade 3 TCAP ELA tier percentages from the 2025 state assessment file.",
            },
            "TX": {
                "below_basic_analog": "Did Not Meet Grade Level",
                "tier_logic": (
                    "Use Texas statewide TAPR Grade 3 RLA thresholds and derive exact tiers by subtraction: "
                    "did_not_meet = 100 - approaches_or_above; "
                    "approaches_only = approaches_or_above - meets_or_above; "
                    "meets_only = meets_or_above - masters; masters = masters."
                ),
            },
            "VA": {
                "below_basic_analog": "Failed",
                "tier_logic": (
                    "Use Virginia School Quality Profiles Grade 3 English Reading statewide bins. "
                    "The public state profile reports Advanced, Proficient, Passed, and Failed; Failed is used as "
                    "the below-basic analog because the public source does not split non-passing students further."
                ),
            },
            "WA": {
                "below_basic_analog": "Level 1",
                "tier_logic": "Use Washington's published statewide Grade 3 SBAC level shares and renormalize them on a tested-only denominator because the public dataset reports shares of all expected students.",
            },
            "WV": {
                "below_basic_analog": "100 - Meets Standard or above",
                "tier_logic": (
                    "Use West Virginia's public 2024 Grade 3 ELA proficiency figure as an official proficiency-only "
                    "proxy. "
                    "The public sources used here did not expose the full statewide tier split without an authenticated dashboard session."
                ),
            },
            "WI": {
                "below_basic_analog": "Developing",
                "tier_logic": "Use Wisconsin's published statewide Grade 3 Forward ELA source bins and renormalize the performance tiers on a tested-only denominator because the public percentages include No Test.",
            },
        },
        "federal_proxy_fill_rule": {
            "description": (
                "Where newer exact statewide tiers were not loaded, fill the below-basic analog from the public "
                "Ed Data Express Grade 3 SEA reading/language arts Percent Proficient row as 100 - Percent Proficient."
            ),
            "states_filled_from_proxy": sorted(proxy_states_added),
            "latest_public_school_year_for_this_filter": "2021-2022",
            "fallbacks": {"UT": "2020-2021"},
            "still_missing_after_proxy_check": still_missing_after_proxy_check,
        },
        "sources": {
            "AK": {
                "source_download_url": AK_SOURCE_DOWNLOAD_URL,
                "source_page_url": AK_SOURCE_PAGE_URL,
            },
            "AR": {
                "source_download_url": AR_SOURCE_DOWNLOAD_URL,
                "source_page_url": AR_SOURCE_PAGE_URL,
            },
            "CA": {
                "source_download_url": CA_SOURCE_DOWNLOAD_URL,
                "source_page_url": CA_SOURCE_PAGE_URL,
            },
            "CO": {
                "source_download_url": CO_SOURCE_DOWNLOAD_URL,
                "source_page_url": CO_SOURCE_PAGE_URL,
            },
            "CT": {
                "source_download_url": CT_SOURCE_DOWNLOAD_URL,
                "source_page_url": CT_SOURCE_PAGE_URL,
            },
            "DC": {
                "source_download_url": DC_SOURCE_DOWNLOAD_URL,
                "source_page_url": DC_SOURCE_PAGE_URL,
            },
            "DE": {
                "source_download_url": DE_SOURCE_DOWNLOAD_URL,
                "source_page_url": DE_SOURCE_PAGE_URL,
            },
            "FL": {
                "source_download_url": FL_SOURCE_DOWNLOAD_URL,
                "source_page_url": FL_SOURCE_PAGE_URL,
            },
            "GA": {
                "source_download_url": GA_SOURCE_DOWNLOAD_URL,
                "source_page_url": GA_SOURCE_PAGE_URL,
            },
            "IN": {
                "source_download_url": IN_SOURCE_DOWNLOAD_URL,
                "source_page_url": IN_SOURCE_PAGE_URL,
            },
            "KY": {
                "source_download_url": KY_SOURCE_DOWNLOAD_URL,
                "source_page_url": KY_SOURCE_PAGE_URL,
            },
            "LA": {
                "source_download_url": LA_SOURCE_DOWNLOAD_URL,
                "source_page_url": LA_SOURCE_PAGE_URL,
            },
            "MD": {
                "source_download_url": MD_SOURCE_DOWNLOAD_URL,
                "source_page_url": MD_SOURCE_PAGE_URL,
            },
            "MA": {
                "source_download_url": MA_SOURCE_DOWNLOAD_URL,
                "source_page_url": MA_SOURCE_PAGE_URL,
            },
            "MS": {
                "source_download_url": MS_SOURCE_DOWNLOAD_URL,
                "source_page_url": MS_SOURCE_PAGE_URL,
            },
            "NH": {
                "source_download_url": NH_SOURCE_DOWNLOAD_URL,
                "source_page_url": NH_SOURCE_PAGE_URL,
            },
            "NC": {
                "source_download_url": NC_SOURCE_DOWNLOAD_URL,
                "source_page_url": NC_SOURCE_PAGE_URL,
            },
            "OH": {
                "source_download_url": OH_SOURCE_INDEX_URL,
                "source_page_url": OH_SOURCE_PAGE_URL,
            },
            "NJ": {
                "source_download_url": NJ_SOURCE_DOWNLOAD_URL,
                "source_page_url": NJ_SOURCE_PAGE_URL,
            },
            "PA": {
                "source_download_url": PA_SOURCE_DOWNLOAD_URL,
                "source_page_url": PA_SOURCE_PAGE_URL,
            },
            "RI": {
                "source_download_url": RI_SOURCE_DOWNLOAD_URL,
                "source_page_url": RI_SOURCE_PAGE_URL,
            },
            "SC": {
                "source_download_url": SC_SOURCE_DOWNLOAD_URL,
                "source_page_url": SC_SOURCE_PAGE_URL,
            },
            "TN": {
                "source_download_url": TN_SOURCE_DOWNLOAD_URL,
                "source_page_url": TN_SOURCE_PAGE_URL,
            },
            "TX": {
                "source_download_url": TX_SOURCE_DOWNLOAD_URL,
                "source_page_url": TX_SOURCE_PAGE_URL,
            },
            "VA": {
                "source_download_url": VA_SOURCE_DOWNLOAD_URL,
                "source_page_url": VA_SOURCE_PAGE_URL,
            },
            "WA": {
                "source_download_url": WA_SOURCE_DOWNLOAD_URL,
                "source_page_url": WA_SOURCE_PAGE_URL,
            },
            "WV": {
                "source_download_url": WV_SOURCE_DOWNLOAD_URL,
                "source_page_url": WV_SOURCE_PAGE_URL,
                "tier_definitions_page_url": WV_TIER_DEFINITIONS_PAGE_URL,
            },
            "WI": {
                "source_download_url": WI_SOURCE_DOWNLOAD_URL,
                "source_page_url": WI_SOURCE_PAGE_URL,
            },
            "FEDERAL_PROXY": {
                "source_page_url": ED_DATA_EXPRESS_SOURCE_PAGE_URL,
                "source_processed_csv": str(ED_DATA_EXPRESS_PROXY_RELATIVE_PATH),
            },
        },
    }
    for state_code, record in OFFICIAL_STATE_RECORDS.items():
        output_key = (
            f"{state_code.lower()}_statewide_tiers_csv"
            if record["record_kind"] == "exact_tiers"
            else f"{state_code.lower()}_public_reference_csv"
        )
        metadata["outputs"][output_key] = str(record["output_path"])
        metadata["state_logic"][state_code] = {
            "below_basic_analog": str(record["below_basic_label"]),
            "tier_logic": str(record["notes"]),
        }
        metadata["sources"][state_code] = {
            "source_download_url": str(record["source_url"]),
            "source_page_url": str(record["source_page_url"]),
        }
    metadata_output_path = repo_root / METADATA_RELATIVE_PATH
    write_json(metadata_output_path, metadata)
    rollout_tracker_output_path = _write_rollout_tracker(
        repo_root,
        below_basic_df=below_basic_df,
        published_reference_df=published_reference_df,
        proxy_df=ed_data_express_proxy_df,
    )

    _update_catalog(
        repo_root,
        [
            {
                "state": "AK",
                "state_name": "Alaska",
                "program": "AK_STAR",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2025 Alaska assessment brief PDF used for statewide Grade 3 AK STAR ELA tiers.",
                "path": str(AK_RAW_RELATIVE_PATH),
                "source_url": AK_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "AK",
                "state_name": "Alaska",
                "program": "AK_STAR",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA AK STAR exact performance tiers.",
                "path": str(AK_OUTPUT_RELATIVE_PATH),
                "source_url": AK_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "AR",
                "state_name": "Arkansas",
                "program": "ATLAS",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2025 Arkansas ATLAS statewide summary workbook.",
                "path": str(AR_RAW_RELATIVE_PATH),
                "source_url": AR_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "AR",
                "state_name": "Arkansas",
                "program": "ATLAS",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA ATLAS exact performance tiers.",
                "path": str(AR_OUTPUT_RELATIVE_PATH),
                "source_url": AR_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "CA",
                "state_name": "California",
                "program": "CAASPP",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2025 California CAASPP statewide Grade 3 ELA workbook with Standard Met/Exceeded.",
                "path": str(CA_RAW_RELATIVE_PATH),
                "source_url": CA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "CA",
                "state_name": "California",
                "program": "CAASPP",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA CAASPP public reference row using California's published Standard Met/Exceeded value.",
                "path": str(CA_OUTPUT_RELATIVE_PATH),
                "source_url": CA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "CO",
                "state_name": "Colorado",
                "program": "CMAS",
                "reporting_period": "2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA CMAS exact performance tiers.",
                "path": str(CO_OUTPUT_RELATIVE_PATH),
                "source_url": CO_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "CT",
                "state_name": "Connecticut",
                "program": "SMARTER_BALANCED",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Saved extract of the public Connecticut EdSight Grade 3 Smarter Balanced ELA statewide report.",
                "path": str(CT_RAW_RELATIVE_PATH),
                "source_url": CT_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "CT",
                "state_name": "Connecticut",
                "program": "SMARTER_BALANCED",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA Connecticut Smarter Balanced exact performance tiers.",
                "path": str(CT_OUTPUT_RELATIVE_PATH),
                "source_url": CT_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "DC",
                "state_name": "District of Columbia",
                "program": "DC_CAPE",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw OSSE state-level workbook for 2024-25 DC CAPE and MSAA results.",
                "path": str(DC_RAW_RELATIVE_PATH),
                "source_url": DC_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "DC",
                "state_name": "District of Columbia",
                "program": "DC_CAPE",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA DC CAPE exact performance tiers.",
                "path": str(DC_OUTPUT_RELATIVE_PATH),
                "source_url": DC_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "DE",
                "state_name": "Delaware",
                "program": "SMARTER_BALANCED",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA public reference row using Delaware's published proficiency figure as an official proxy.",
                "path": str(DE_OUTPUT_RELATIVE_PATH),
                "source_url": DE_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "NH",
                "state_name": "New Hampshire",
                "program": "NH_SAS",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA public reference row using New Hampshire's published proficiency rate.",
                "path": str(NH_OUTPUT_RELATIVE_PATH),
                "source_url": NH_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "OH",
                "state_name": "Ohio",
                "program": "OHIO_STATE_TESTS",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw Ohio School Report Cards Title 1 Proficiency by Grade workbook for 2024-2025.",
                "path": str(OH_RAW_RELATIVE_PATH),
                "source_url": OH_SOURCE_INDEX_URL,
            },
            {
                "state": "OH",
                "state_name": "Ohio",
                "program": "OHIO_STATE_TESTS",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA public reference row using Ohio's published Percent Proficient or Above value.",
                "path": str(OH_OUTPUT_RELATIVE_PATH),
                "source_url": OH_SOURCE_INDEX_URL,
            },
            {
                "state": "FL",
                "state_name": "Florida",
                "program": "FAST",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw statewide-and-district Grade 3 FAST ELA PM3 workbook.",
                "path": str(FL_RAW_RELATIVE_PATH),
                "source_url": FL_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "FL",
                "state_name": "Florida",
                "program": "FAST",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA FAST exact performance tiers.",
                "path": str(FL_OUTPUT_RELATIVE_PATH),
                "source_url": FL_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "GA",
                "state_name": "Georgia",
                "program": "GEORGIA_MILESTONES",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2025 Georgia Milestones Grade 3 statewide summary workbook.",
                "path": str(GA_RAW_RELATIVE_PATH),
                "source_url": GA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "GA",
                "state_name": "Georgia",
                "program": "GEORGIA_MILESTONES",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA Georgia Milestones exact performance tiers.",
                "path": str(GA_OUTPUT_RELATIVE_PATH),
                "source_url": GA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "IN",
                "state_name": "Indiana",
                "program": "ILEARN",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2025 ILEARN Grade 3-8 statewide summary workbook.",
                "path": str(IN_RAW_RELATIVE_PATH),
                "source_url": IN_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "IN",
                "state_name": "Indiana",
                "program": "ILEARN",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA ILEARN exact tiers derived from published statewide counts.",
                "path": str(IN_OUTPUT_RELATIVE_PATH),
                "source_url": IN_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "KY",
                "state_name": "Kentucky",
                "program": "KSA",
                "reporting_period": "2023-2024",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 Reading KSA exact performance tiers.",
                "path": str(KY_OUTPUT_RELATIVE_PATH),
                "source_url": KY_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "LA",
                "state_name": "Louisiana",
                "program": "LEAP",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2025 State LEA LEAP achievement-level summary workbook.",
                "path": str(LA_RAW_RELATIVE_PATH),
                "source_url": LA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "LA",
                "state_name": "Louisiana",
                "program": "LEAP",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA LEAP exact performance tiers.",
                "path": str(LA_OUTPUT_RELATIVE_PATH),
                "source_url": LA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "MD",
                "state_name": "Maryland",
                "program": "MCAP",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Saved extract of the public Maryland Report Card JSON response for statewide 2025 Grade 3 MCAP ELA performance levels.",
                "path": str(MD_RAW_RELATIVE_PATH),
                "source_url": MD_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "MD",
                "state_name": "Maryland",
                "program": "MCAP",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA MCAP exact performance tiers.",
                "path": str(MD_OUTPUT_RELATIVE_PATH),
                "source_url": MD_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "MA",
                "state_name": "Massachusetts",
                "program": "MCAS",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw statewide 2025 Massachusetts MCAS achievement-level state profile HTML.",
                "path": str(MA_RAW_RELATIVE_PATH),
                "source_url": MA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "MA",
                "state_name": "Massachusetts",
                "program": "MCAS",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA MCAS exact performance tiers.",
                "path": str(MA_OUTPUT_RELATIVE_PATH),
                "source_url": MA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "MS",
                "state_name": "Mississippi",
                "program": "MAAP",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA MAAP exact performance tiers.",
                "path": str(MS_OUTPUT_RELATIVE_PATH),
                "source_url": MS_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "NC",
                "state_name": "North Carolina",
                "program": "NC_EOG",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2024-25 North Carolina statewide assessment and indicator workbook.",
                "path": str(NC_RAW_RELATIVE_PATH),
                "source_url": NC_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "NC",
                "state_name": "North Carolina",
                "program": "NC_EOG",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 reading source bins with Levels 1 and 2 aggregated into Not Proficient.",
                "path": str(NC_OUTPUT_RELATIVE_PATH),
                "source_url": NC_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "NJ",
                "state_name": "New Jersey",
                "program": "NJSLA",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2024-25 New Jersey Grade 3 ELA statewide results workbook.",
                "path": str(NJ_RAW_RELATIVE_PATH),
                "source_url": NJ_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "NJ",
                "state_name": "New Jersey",
                "program": "NJSLA",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA NJSLA exact performance tiers.",
                "path": str(NJ_OUTPUT_RELATIVE_PATH),
                "source_url": NJ_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "NY",
                "state_name": "New York",
                "program": "NYSED_REPORT_CARD",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA New York State exact performance tiers from the NYSED Report Card Database.",
                "path": str(NY_OUTPUT_RELATIVE_PATH),
                "source_url": NY_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "PA",
                "state_name": "Pennsylvania",
                "program": "PSSA",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw Pennsylvania assessment reporting page HTML used for statewide Grade 3 PSSA ELA parsing.",
                "path": str(PA_RAW_RELATIVE_PATH),
                "source_url": PA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "PA",
                "state_name": "Pennsylvania",
                "program": "PSSA",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA PSSA exact performance tiers.",
                "path": str(PA_OUTPUT_RELATIVE_PATH),
                "source_url": PA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "RI",
                "state_name": "Rhode Island",
                "program": "RICAS",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Saved extract of the public Rhode Island Assessment Data Portal Grade 3 RICAS ELA statewide report.",
                "path": str(RI_RAW_RELATIVE_PATH),
                "source_url": RI_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "RI",
                "state_name": "Rhode Island",
                "program": "RICAS",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA Rhode Island RICAS exact performance tiers.",
                "path": str(RI_OUTPUT_RELATIVE_PATH),
                "source_url": RI_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "SC",
                "state_name": "South Carolina",
                "program": "SC_READY",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA SC READY exact performance tiers.",
                "path": str(SC_OUTPUT_RELATIVE_PATH),
                "source_url": SC_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "TN",
                "state_name": "Tennessee",
                "program": "TCAP",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2025 Tennessee state assessment file with Grade 3 ELA tiers.",
                "path": str(TN_RAW_RELATIVE_PATH),
                "source_url": TN_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "TN",
                "state_name": "Tennessee",
                "program": "TCAP",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA TCAP exact performance tiers.",
                "path": str(TN_OUTPUT_RELATIVE_PATH),
                "source_url": TN_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "TX",
                "state_name": "Texas",
                "program": "STAAR",
                "reporting_period": "2023-2024",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw statewide TAPR Grade 3 STAAR workbook.",
                "path": str(TX_RAW_RELATIVE_PATH),
                "source_url": TX_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "TX",
                "state_name": "Texas",
                "program": "STAAR",
                "reporting_period": "2023-2024",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 RLA STAAR exact tiers derived from public threshold rates.",
                "path": str(TX_OUTPUT_RELATIVE_PATH),
                "source_url": TX_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "TX",
                "state_name": "Texas",
                "program": "STAAR",
                "reporting_period": "2023-2024",
                "kind": "metadata",
                "granularity": "state+district",
                "description": "Guide to selected Texas Grade 3 STAAR field names used in this repo.",
                "path": str(TX_FIELD_GUIDE_RELATIVE_PATH),
                "source_url": TX_SOURCE_PAGE_URL,
            },
            {
                "state": "VA",
                "state_name": "Virginia",
                "program": "SOL",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw Virginia School Quality Profiles state report page used for Grade 3 English Reading parsing.",
                "path": str(VA_RAW_RELATIVE_PATH),
                "source_url": VA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "VA",
                "state_name": "Virginia",
                "program": "SOL",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 English Reading public source bins from Virginia School Quality Profiles.",
                "path": str(VA_OUTPUT_RELATIVE_PATH),
                "source_url": VA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "WA",
                "state_name": "Washington",
                "program": "SBAC",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Washington state assessment extract used for statewide Grade 3 ELA SBAC processing.",
                "path": str(WA_RAW_RELATIVE_PATH),
                "source_url": WA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "WA",
                "state_name": "Washington",
                "program": "SBAC",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA SBAC exact tiers renormalized on a tested-only denominator.",
                "path": str(WA_OUTPUT_RELATIVE_PATH),
                "source_url": WA_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "WV",
                "state_name": "West Virginia",
                "program": "WVGSA",
                "reporting_period": "2023-2024",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA WVGSA public reference row with proficiency only, used as an official proxy because the full tier split was not exposed in the public source used here.",
                "path": str(WV_REFERENCE_OUTPUT_RELATIVE_PATH),
                "source_url": WV_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "WI",
                "state_name": "Wisconsin",
                "program": "FORWARD",
                "reporting_period": "2024-2025",
                "kind": "raw",
                "granularity": "state",
                "description": "Raw 2024-25 Wisconsin Forward certified statewide file bundle.",
                "path": str(WI_RAW_RELATIVE_PATH),
                "source_url": WI_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "WI",
                "state_name": "Wisconsin",
                "program": "FORWARD",
                "reporting_period": "2024-2025",
                "kind": "processed",
                "granularity": "state",
                "description": "Statewide Grade 3 ELA Forward exact tiers renormalized on a tested-only denominator.",
                "path": str(WI_OUTPUT_RELATIVE_PATH),
                "source_url": WI_SOURCE_DOWNLOAD_URL,
            },
            {
                "state": "MULTI",
                "state_name": "Multiple States",
                "program": "ED_DATA_EXPRESS",
                "reporting_period": "2020-2021 to 2021-2022",
                "kind": "processed",
                "granularity": "state",
                "description": "Federal Ed Data Express Grade 3 statewide reading/language arts proficiency rows used as below-basic proxy fills for states missing newer exact tiers.",
                "path": str(ED_DATA_EXPRESS_PROXY_RELATIVE_PATH),
                "source_url": ED_DATA_EXPRESS_SOURCE_PAGE_URL,
            },
            {
                "state": "MULTI",
                "state_name": "Multiple States",
                "program": "GRADE3_ELA_TIERS",
                "reporting_period": "2023-2025 mixed",
                "kind": "processed",
                "granularity": "state",
                "description": "Cross-state Grade 3 ELA tier comparison where exact statewide tiers are available.",
                "path": str(SUMMARY_RELATIVE_PATH),
                "source_url": "",
            },
            {
                "state": "MULTI",
                "state_name": "Multiple States",
                "program": "GRADE3_ELA_TIERS",
                "reporting_period": "2023-2025 mixed",
                "kind": "processed",
                "granularity": "state",
                "description": "Cross-state below-basic analog summary for Grade 3 ELA.",
                "path": str(BELOW_BASIC_RELATIVE_PATH),
                "source_url": "",
            },
            {
                "state": "MULTI",
                "state_name": "Multiple States",
                "program": "GRADE3_ELA_TIERS",
                "reporting_period": "2023-2025 mixed",
                "kind": "processed",
                "granularity": "state",
                "description": "Lightweight reference table of the published source bins for statewide Grade 3 ELA.",
                "path": str(PUBLISHED_REFERENCE_RELATIVE_PATH),
                "source_url": "",
            },
            {
                "state": "MULTI",
                "state_name": "Multiple States",
                "program": "GRADE3_ELA_TIERS",
                "reporting_period": "2023-2025 mixed",
                "kind": "metadata",
                "granularity": "state",
                "description": "Rollout tracker for statewide Grade 3 ELA state coverage.",
                "path": str(ROLLOUT_TRACKER_RELATIVE_PATH),
                "source_url": "",
            },
        ],
    )
    _update_catalog(repo_root, official_state_catalog_entries)

    outputs = {
        "alaska_statewide_tiers": repo_root / AK_OUTPUT_RELATIVE_PATH,
        "arkansas_statewide_tiers": repo_root / AR_OUTPUT_RELATIVE_PATH,
        "california_public_reference": repo_root / CA_OUTPUT_RELATIVE_PATH,
        "colorado_statewide_tiers": repo_root / CO_OUTPUT_RELATIVE_PATH,
        "connecticut_statewide_tiers": repo_root / CT_OUTPUT_RELATIVE_PATH,
        "dc_cape_statewide_tiers": repo_root / DC_OUTPUT_RELATIVE_PATH,
        "delaware_public_reference": repo_root / DE_OUTPUT_RELATIVE_PATH,
        "florida_statewide_tiers": repo_root / FL_OUTPUT_RELATIVE_PATH,
        "georgia_statewide_tiers": repo_root / GA_OUTPUT_RELATIVE_PATH,
        "indiana_statewide_tiers": repo_root / IN_OUTPUT_RELATIVE_PATH,
        "kentucky_statewide_tiers": repo_root / KY_OUTPUT_RELATIVE_PATH,
        "louisiana_statewide_tiers": repo_root / LA_OUTPUT_RELATIVE_PATH,
        "maryland_statewide_tiers": repo_root / MD_OUTPUT_RELATIVE_PATH,
        "massachusetts_statewide_tiers": repo_root / MA_OUTPUT_RELATIVE_PATH,
        "mississippi_statewide_tiers": repo_root / MS_OUTPUT_RELATIVE_PATH,
        "new_jersey_statewide_tiers": repo_root / NJ_OUTPUT_RELATIVE_PATH,
        "new_york_statewide_tiers": repo_root / NY_OUTPUT_RELATIVE_PATH,
        "north_carolina_public_bins": repo_root / NC_OUTPUT_RELATIVE_PATH,
        "ohio_public_reference": repo_root / OH_OUTPUT_RELATIVE_PATH,
        "rollout_tracker": rollout_tracker_output_path,
        "rhode_island_statewide_tiers": repo_root / RI_OUTPUT_RELATIVE_PATH,
        "south_carolina_statewide_tiers": repo_root / SC_OUTPUT_RELATIVE_PATH,
        "tennessee_statewide_tiers": repo_root / TN_OUTPUT_RELATIVE_PATH,
        "texas_statewide_tiers": repo_root / TX_OUTPUT_RELATIVE_PATH,
        "virginia_public_bins": repo_root / VA_OUTPUT_RELATIVE_PATH,
        "washington_statewide_tiers": repo_root / WA_OUTPUT_RELATIVE_PATH,
        "west_virginia_public_reference": repo_root / WV_REFERENCE_OUTPUT_RELATIVE_PATH,
        "wisconsin_statewide_tiers": repo_root / WI_OUTPUT_RELATIVE_PATH,
        "cross_state_tiers": summary_output_path,
        "below_basic_analog": below_basic_output_path,
        "published_reference_bins": published_reference_output_path,
        "ed_data_express_proxy_source": repo_root / ED_DATA_EXPRESS_PROXY_RELATIVE_PATH,
        "texas_field_guide": repo_root / TX_FIELD_GUIDE_RELATIVE_PATH,
        "metadata": metadata_output_path,
    }
    outputs.update(official_state_outputs)
    return outputs

# State Assessment Datasets

This repo now has a clearer primary goal: a small, readable cross-state comparison of statewide Grade 3 ELA performance tiers.

## Static Dashboard

The colleague-facing dashboard is in `docs/` and is designed for GitHub Pages. It includes:

- coverage cards for state-published and federal-proxy data
- a clickable national source-quality map
- state assessment results, reporting years, source notes, and official links
- source-quality filters, state search, and a sortable source register
- full and filtered CSV downloads

Build its compact data bundle after refreshing the assessment outputs:

```bash
python build_dashboard_data.py
```

Preview it locally:

```bash
python3 -m http.server 8000 --directory docs
```

Then open `http://localhost:8000`. The GitHub Actions workflow in
`.github/workflows/pages.yml` rebuilds and publishes the site whenever the dashboard or summary data changes on `main`.

The recommended workflow is the focused builder:

```bash
python build_statewide_grade3_ela_tiers.py
```

That produces:

- a long-form tier file for Arkansas, Colorado, Florida, Georgia, Indiana, Kentucky, Louisiana, Mississippi, New Jersey, South Carolina, Tennessee, Texas, Washington, and Wisconsin
- a tiny cross-state summary of the `below basic` analog
- a tiny CEO-friendly reference table of the original published source bins
- a Looker-ready long comparison table that repeats NAEP national benchmark rows for each state context
- public-reference rows for Delaware and West Virginia when the public source exposes proficiency but not the full statewide tier split
- a North Carolina source-bin row where `Not Proficient` aggregates Levels 1 and 2
- a Texas field guide that explains the coded STAAR column names
- a rollout tracker showing covered, queued, and reference-only states

## Recommended Outputs

- `datasets/summary/statewide_grade3_ela_tiers.csv`
- `datasets/summary/statewide_grade3_ela_below_basic_analog.csv`
- `datasets/summary/statewide_grade3_ela_published_reference_bins.csv`
- `datasets/summary/statewide_grade3_ela_rollout_tracker.csv`
- `datasets/summary/state_assessment_vs_naep_looker_minimal.csv`
- `datasets/summary/state_assessment_vs_naep_looker_enriched.csv`
- `datasets/ar/atlas/2024_2025/processed/atlas_2025_statewide_grade3_ela_tiers.csv`
- `datasets/co/cmas/2025/processed/cmas_2025_statewide_grade3_ela_tiers.csv`
- `datasets/de/dessa/2024_2025/processed/dessa_2025_statewide_grade3_ela_public_reference.csv`
- `datasets/fl/fast/2024_2025/processed/fast_2025_statewide_grade3_ela_tiers.csv`
- `datasets/ga/georgia_milestones/2024_2025/processed/georgia_milestones_2025_statewide_grade3_ela_tiers.csv`
- `datasets/in/ilearn/2024_2025/processed/ilearn_2025_statewide_grade3_ela_tiers.csv`
- `datasets/ky/ksa/2023_2024/processed/ksa_2024_statewide_grade3_reading_tiers.csv`
- `datasets/la/leap/2024_2025/processed/leap_2025_statewide_grade3_ela_tiers.csv`
- `datasets/ma/mcas/2024_2025/processed/mcas_2025_statewide_grade3_ela_tiers.csv`
- `datasets/ms/maap/2024_2025/processed/maap_2025_statewide_grade3_ela_tiers.csv`
- `datasets/nc/eog/2024_2025/processed/eog_2025_statewide_grade3_reading_public_bins.csv`
- `datasets/nh/nh_sas/2024_2025/processed/nh_sas_2025_statewide_grade3_ela_public_reference.csv`
- `datasets/nj/njsla/2024_2025/processed/njsla_2025_statewide_grade3_ela_tiers.csv`
- `datasets/sc/sc_ready/2024_2025/processed/sc_ready_2025_statewide_grade3_ela_tiers.csv`
- `datasets/tn/tcap/2024_2025/processed/tcap_2025_statewide_grade3_ela_tiers.csv`
- `datasets/tx/staar/2023_2024/processed/staar_2024_statewide_grade3_rla_tiers.csv`
- `datasets/wa/sbac/2024_2025/processed/sbac_2025_statewide_grade3_ela_tiers.csv`
- `datasets/wv/wvgsa/2023_2024/processed/wvgsa_2024_statewide_grade3_ela_public_reference.csv`
- `datasets/wi/forward/2024_2025/processed/forward_2025_statewide_grade3_ela_tiers.csv`
- `datasets/tx/staar/2023_2024/metadata/staar_grade3_field_guide.csv`

## Why This Shape

States do not publish performance tiers in the same way.

- Arkansas ATLAS publishes exact statewide Grade 3 ELA percentages for Levels 1 through 4.
- Colorado CMAS publishes exact statewide percentages for each performance tier.
- Delaware's public statewide row used here exposes Grade 3 ELA proficiency only.
- Florida FAST publishes exact statewide Grade 3 PM3 percentages for Levels 1 through 5.
- Georgia Milestones publishes exact statewide Grade 3 ELA percentages for Beginning, Developing, Proficient, and Distinguished Learner.
- Indiana ILEARN publishes statewide counts for each performance tier, so this repo converts those counts to percentages.
- Kentucky KSA publishes exact statewide percentages for each performance tier.
- Louisiana LEAP publishes exact statewide percentages for each achievement level.
- Massachusetts MCAS publishes the statewide Grade 3 ELA achievement-level split directly on the state profile page.
- Mississippi MAAP publishes exact statewide percentages for each performance level in the annual executive summary.
- New Hampshire's public iPlatform assessment report exposes the statewide Grade 3 NH SAS ELA proficiency rate but not the full performance-level split used here.
- New Jersey NJSLA publishes exact statewide Grade 3 ELA percentages for Levels 1 through 5.
- North Carolina publishes statewide Grade 3 reading source bins where `Not Proficient` combines Levels 1 and 2.
- South Carolina SC READY publishes exact statewide percentages for each performance tier on the public state results page.
- Tennessee TCAP publishes exact statewide percentages for each performance tier in the state assessment file.
- Texas STAAR commonly publishes cumulative thresholds such as `Approaches Grade Level or above`, `Meets Grade Level or above`, and `Masters Grade Level`.
- Washington SBAC publishes statewide level shares as fractions of all expected students, so this repo renormalizes them on a tested-only denominator.
- West Virginia WVGSA publicly exposes the grade 3 ELA proficiency rate in the public PDF we used here, but not the full statewide tier split.
- Wisconsin Forward publishes statewide source bins that include `No Test`, so this repo renormalizes the performance levels on a tested-only denominator.

So for Texas, this repo derives exact tiers as:

```text
did_not_meet = 100 - approaches_or_above
approaches_only = approaches_or_above - meets_or_above
meets_only = meets_or_above - masters
masters = masters
```

That makes Texas readable and comparable without pretending the raw TEA field names are self-explanatory.

## Current Interpretation Choice

For the cross-state `below basic` analog:

- Arkansas uses `Level 1`
- Colorado uses `Did Not Yet Meet Expectations`
- Florida uses `Level 1`
- Georgia uses `Beginning Learner`
- Indiana uses `Below Proficiency`
- Kentucky uses `Novice`
- Louisiana uses `Unsatisfactory`
- Mississippi uses `Minimal`
- New Jersey uses `Level 1`
- New Hampshire uses `100 - Percent Proficient` as a clearly labeled state-published proxy
- North Carolina uses `Not Proficient`
- South Carolina uses `Does Not Meet Expectations`
- Tennessee uses `Below`
- Texas uses `Did Not Meet Grade Level`
- Washington uses `Level 1`
- Wisconsin uses `Developing`
- West Virginia is not included in the strict below-basic summary yet because the public source we used exposed proficiency but not the full statewide tier split.

This is intentionally strict. It does not roll Colorado `Partially Met` or `Approached` into the below-basic bucket.

If you want the untouched source view for quick review, use:

- `datasets/summary/statewide_grade3_ela_published_reference_bins.csv`

That file keeps:

- Arkansas in its four published ATLAS tiers
- Colorado in its five published CMAS tiers
- Delaware in a clearly labeled public proficiency-only reference row
- Florida in its five published FAST levels
- Georgia in its four published Georgia Milestones tiers
- Indiana in its four published ILEARN tiers
- Kentucky in its four published KSA tiers
- Louisiana in its five published LEAP achievement levels
- Massachusetts in a clearly labeled public proficiency-only reference row
- Mississippi in its five published MAAP performance levels
- New Jersey in its five published NJSLA tiers
- New Hampshire in a clearly labeled public proficiency-only reference row
- North Carolina in its four published statewide reading bins
- South Carolina in its four published SC READY performance tiers
- Tennessee in its four published TCAP tiers
- Texas in its three published STAAR thresholds
- Washington in its published Level 1-4 plus `No Score` bins
- West Virginia in a clearly labeled public proficiency-only reference row
- Wisconsin in its published Forward bins including `No Test`

## Looker Studio Shape

If you want something easy to load into Looker Studio, start with:

- `datasets/summary/state_assessment_vs_naep_looker_minimal.csv`

That file uses the simple long shape:

```text
state, year, grade, subject, source, assessment, metric, value
```

Examples:

- `Colorado, 2024, 4, Reading, NAEP (State), NAEP, Percent Below Basic, 35.12`
- `Colorado, 2024, 4, Reading, NAEP (National Public), NAEP, Percent Below Basic, 40.67`
- `Colorado, 2025, 3, ELA, CMAS, CMAS, Percent in Below-Basic Analog Tier, 22.4`

The richer companion file is:

- `datasets/summary/state_assessment_vs_naep_looker_enriched.csv`

That version adds helper columns such as:

- `state_code`
- `school_year`
- `comparison_role`
- `jurisdiction_of_measure`
- `source_url`
- `notes`

The repeated `NAEP (National Public)` rows are intentional. They let a simple state filter in Looker Studio still show the national comparison row without requiring a join.

Important year note:

- NAEP rows are 2024 Grade 4 Reading.
- Kentucky, Texas, and West Virginia state rows here are 2024.
- Arkansas, Colorado, Delaware, Florida, Georgia, Indiana, Louisiana, Massachusetts, Mississippi, New Hampshire, New Jersey, North Carolina, South Carolina, Tennessee, Washington, and Wisconsin state rows here are 2025 because those are the latest state files currently loaded in this repo.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you already have the raw source files locally, you can point the focused builder at them:

```bash
python build_statewide_grade3_ela_tiers.py \
  --ar-raw-workbook /path/to/2025_arkansas_atlas.xlsx \
  --co-raw-workbook /path/to/2025_cmas_workbook.xlsx \
  --fl-raw-workbook /path/to/2025_fast_grade3_ela.xls \
  --ga-raw-workbook /path/to/2025_georgia_milestones_grade3.xlsx \
  --in-raw-workbook /path/to/2025_ilearn_statewide_summary.xlsx \
  --la-raw-workbook /path/to/2025_leap_state_lea_achievement_levels.xlsx \
  --nc-raw-workbook /path/to/2025_nc_assessment_workbook.xlsx \
  --nj-raw-workbook /path/to/2025_njsla_grade3_ela.xlsx \
  --tn-raw-workbook /path/to/2025_tcap_state_assessment.xlsx \
  --tx-raw-workbook /path/to/tx_statewide_grade3_staar.xlsx \
  --wa-raw-csv /path/to/wa_state_assessment_extract.csv \
  --wi-raw-zip /path/to/wi_forward_certified.zip
```

## Broader Extracts

The broader state-organized extractor is still available if we want to return to district-level or larger pulls later:

```bash
python build_state_assessment_datasets.py
```

Those outputs remain useful, but they are now secondary to the smaller statewide Grade 3 ELA comparison.

## Layout

```text
datasets/
  catalog.csv
  summary/
  ar/
    atlas/
      2024_2025/
        raw/
        processed/
  co/
    cmas/
      2025/
        raw/
        processed/
        metadata/
  de/
    dessa/
      2024_2025/
        processed/
  fl/
    fast/
      2024_2025/
        raw/
        processed/
  ga/
    georgia_milestones/
      2024_2025/
        raw/
        processed/
  in/
    ilearn/
      2024_2025/
        raw/
        processed/
  ky/
    ksa/
      2023_2024/
        processed/
  la/
    leap/
      2024_2025/
        raw/
        processed/
  ma/
    mcas/
      2024_2025/
        processed/
  ms/
    maap/
      2024_2025/
        processed/
  nc/
    eog/
      2024_2025/
        raw/
        processed/
  nj/
    njsla/
      2024_2025/
        raw/
        processed/
  sc/
    sc_ready/
      2024_2025/
        processed/
  tn/
    tcap/
      2024_2025/
        raw/
        processed/
  tx/
    staar/
      2023_2024/
        raw/
        processed/
        metadata/
  wa/
    sbac/
      2024_2025/
        raw/
        processed/
  wv/
    wvgsa/
      2023_2024/
        processed/
  wi/
    forward/
      2024_2025/
        raw/
        processed/
state_assessment_data/
  statewide_grade3_ela.py
build_statewide_grade3_ela_tiers.py
build_state_assessment_datasets.py
```

## Source Notes

- Arkansas source: the public 2025 ATLAS statewide summary workbook posted by the Arkansas Department of Education.
- Colorado source: the public CMAS district and school achievement workbook posted on the Colorado Department of Education results page.
- Delaware source: the public statewide Grade 3 ELA proficiency row from Delaware's assessment data export.
- Florida source: the public Grade 3 FAST ELA PM3 district report workbook posted on the Florida Department of Education results page and mirrored on `origin.fldoe.org`.
- Georgia source: the public 2025 Georgia Milestones Grade 3 statewide summary workbook.
- Indiana source: the public 2025 ILEARN Grade 3-8 statewide summary workbook posted on the Indiana Department of Education data center page.
- Kentucky source: the public KSA yearbook PDF published by the Kentucky Department of Education.
- Louisiana source: the public Spring 2025 LEAP State LEA achievement level summary workbook posted on the Louisiana Department of Education results library.
- Massachusetts source: the public 2025 MCAS statewide summary PDF.
- Mississippi source: the public 2025 MAAP executive summary PDF published by the Mississippi Department of Education.
- New Jersey source: the public 2024-25 Grade 3 ELA NJSLA workbook posted by the New Jersey Department of Education.
- North Carolina source: the public 2024-25 school assessment and other indicator workbook posted by the North Carolina Department of Public Instruction.
- South Carolina source: the public 2025 SC READY statewide grade-level results page.
- Tennessee source: the public 2025 state assessment file posted on the Tennessee Department of Education data downloads page.
- Texas source: the public TAPR statewide Grade 3 STAAR export on `rptsvr1.tea.texas.gov`.
- Washington source: the public Washington state assessment dataset, using a state-level Grade 3 ELA extract and tested-only renormalization.
- West Virginia source: the public 2024 statewide assessment PDF linked from the WVDE August 2024 board meeting page.
- Wisconsin source: the public 2024-25 Forward certified statewide file bundle, with tested-only renormalization because the published bins include `No Test`.

## Legacy Files

The older Colorado-only dashboard files are still here:

- `fetch_cmas_co.py`
- `app.py`
- `data/`

# Looker Studio Quick Start

Use [state_assessment_vs_naep_looker_minimal.csv](/Users/jennymiller/code/ColoradoCMAS/datasets/summary/state_assessment_vs_naep_looker_minimal.csv) if you want the cleanest import.

Recommended first table:

- Dimension: `state`
- Dimension: `source`
- Dimension: `metric`
- Metric: `value`
- Filters: `state`, `year`

Recommended side-by-side chart:

- Dimension: `source`
- Breakdown dimension: `metric`
- Metric: `value`
- Filter to one `state`
- Filter `metric` to:
  - `Percent Below Basic`
  - `Percent in Below-Basic Analog Tier`

Use [state_assessment_vs_naep_looker_enriched.csv](/Users/jennymiller/code/ColoradoCMAS/datasets/summary/state_assessment_vs_naep_looker_enriched.csv) if you want more control over filtering.

Helpful enriched fields:

- `comparison_role`
- `jurisdiction_of_measure_name`
- `benchmark_label`
- `notes`

Good starter filters in the enriched file:

- `comparison_role = naep_state`
- `comparison_role = naep_national_public_benchmark`
- `comparison_role = state_assessment`
- `comparison_role = state_assessment_reference`

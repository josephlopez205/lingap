# GAP Hunter — Rule Definitions (v1, Phase 3)

## Data availability note
Barangay-level senior citizen counts (60+), school enrollment, and classroom
counts are not available for the pilot LGU (Rodriguez, Rizal) — PSA has not
published barangay-level age-bracket breakdowns for this municipality as of
this build. Rules below are adapted to use verified real data
(`population_total`, facility geolocation) rather than fabricated figures.

## Rule 1: Health Access Gap
- **Rule ID**: `HEALTH_ACCESS_POPULATION`
- **Sector**: Health
- **Original spec (US-09)**: senior population > 200 AND nearest health
  center > 3km
- **Adapted logic**: total barangay population > [THRESHOLD] AND nearest
  operational health facility > 3km (Haversine/PostGIS geography distance)
- **Rationale for substitution**: senior-specific population data unavailable
  at barangay level; total population is a defensible general-access proxy
  and is real PSA-derived data (via PhilAtlas), not fabricated
- **UI label**: "Health Access Gap" (not "Senior Health Access Gap")

## Rule 2: Education Access Gap
- **Rule ID**: `EDU_ACCESS_POPULATION`
- **Sector**: Education
- **Original spec (US-10)**: classroom:student ratio > 45:1
- **Adapted logic**: total barangay population > [THRESHOLD] AND zero
  schools within 3km (same mechanic as Rule 1, filtered to facility_type='school')
- **Rationale for substitution**: enrollment/classroom-count data not
  captured in current facilities schema; access-based gap (no school nearby)
  is a real, data-backed and equally legitimate planning signal
- **UI label**: "Education Access Gap"

## Severity Score (adapted from US-14)
- **Original spec**: 0.5 × population + 0.3 × deficit + 0.2 × poverty
- **Adapted formula**: 0.6 × normalized population affected + 0.4 ×
  normalized distance deficit
- **Rationale for substitution**: poverty_incidence_pct only available at
  municipal level (7.37%, uniform across all barangays) — including it as a
  weighted term would add false precision, since it wouldn't actually
  differentiate barangays from each other
- **Formula**:
pop_component = (affected_population / max_population_in_lgu) × 100
deficit_ratio = min(nearest_facility_km / distance_threshold_km, 3)
deficit_component = (deficit_ratio / 3) × 100
severity_score = (0.6 × pop_component) + (0.4 × deficit_component)


## Thresholds (tunable, set based on pilot LGU's actual distribution)
- `HEALTH_POPULATION_THRESHOLD` = 10000
- `EDUCATION_POPULATION_THRESHOLD` = 10000
- `DISTANCE_THRESHOLD_KM` = 3.0 (kept as originally specified — this value
  didn't depend on missing data)

## UI Copy Reference

Health Access Gap explanation template:
"This barangay has {population} residents, but the nearest health facility
is {distance}km away — exceeding the {threshold}km access standard."

Education Access Gap explanation template:
"This barangay has {population} residents, but the nearest school is
{distance}km away — exceeding the {threshold}km access standard."

Methodology footnote (for detail cards / reports):
"Gap analysis uses total population as an access-need proxy. Age-specific
and enrollment-specific breakdowns will be incorporated pending PSA data
availability for this municipality."

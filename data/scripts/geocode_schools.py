"""
Geocode DepEd schools (public + private) for Rodriguez, Rizal using Nominatim (OSM).
Saves progress after every row so a crash never loses completed geocoding work.
Re-running this script skips rows that are already in the output file.
"""

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os

INPUT_PATH = "../raw/facilities/v_activefacilities_montalban_educ.csv"
OUTPUT_PATH = "../processed/facilities_schools.csv"

# --- Load source data ---
df = pd.read_csv(INPUT_PATH, encoding="latin1")
df.columns = df.columns.str.strip()  # strip whitespace from headers defensively

print("Columns found:", df.columns.tolist())
print(f"Total rows in source: {len(df)}")

def build_address(row):
    addr = str(row["Address"]).strip() if pd.notna(row["Address"]) else ""
    return f"{addr}, Rodriguez, Rizal, Philippines"

df["full_address"] = df.apply(build_address, axis=1)

# --- Geocoder setup ---
geolocator = Nominatim(user_agent="lingap_school_geocoder", timeout=10)
geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1.1,
    max_retries=1,
    error_wait_seconds=2.0,
)

TOWN_CENTER = (14.7145018, 121.1424623)  # Rodriguez Poblacion fallback

def try_geocode(full_address, school_name):
    try:
        location = geocode(full_address)
        if location:
            return location.latitude, location.longitude, "address_level"
    except Exception:
        pass
    try:
        fallback = f"{school_name}, Rodriguez, Rizal, Philippines"
        location = geocode(fallback)
        if location:
            return location.latitude, location.longitude, "name_level"
    except Exception:
        pass
    return TOWN_CENTER[0], TOWN_CENTER[1], "town_center_fallback"

# --- Resume support: if output file already exists, skip already-geocoded rows ---
if os.path.exists(OUTPUT_PATH):
    existing = pd.read_csv(OUTPUT_PATH)
    done_names = set(existing["facility_name"])
    print(f"Found existing output with {len(existing)} rows already geocoded — resuming.")
else:
    existing = pd.DataFrame(columns=[
        "facility_name", "facility_type", "school_subtype",
        "coc", "address", "lat", "lng", "geocode_precision"
    ])
    done_names = set()

results = [existing]

# --- Main geocoding loop ---
for i, row in df.iterrows():
    name = row["School Name"]
    if name in done_names:
        continue  # already geocoded in a previous run

    lat, lng, precision = try_geocode(row["full_address"], name)
    print(f"[{i+1}/{len(df)}] {str(name)[:50]:50s} -> {precision}")

    new_row = pd.DataFrame([{
        "facility_name": name,
        "facility_type": "school",
        "school_subtype": row.get("Public/Private", ""),
        "coc": row.get("COC", ""),
        "address": row["Address"],
        "lat": lat,
        "lng": lng,
        "geocode_precision": precision,
    }])
    results.append(new_row)

    # Save after EVERY row so a crash never loses progress
    pd.concat(results, ignore_index=True).to_csv(OUTPUT_PATH, index=False)

# --- Final summary ---
final = pd.concat(results, ignore_index=True)
print(f"\nDone. Saved to {OUTPUT_PATH}")
print(f"Total rows: {len(final)}")
print(final["geocode_precision"].value_counts())

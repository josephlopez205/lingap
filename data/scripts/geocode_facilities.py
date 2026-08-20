"""
Geocode DOH NHFR health facilities for Rodriguez, Rizal using Nominatim (OSM).
Builds an address string per row, geocodes it, and writes lat/lng + a cleaned
output CSV matching the `facilities` table schema.
"""

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

INPUT_PATH = "../raw/facilities/v_activefacilities_montalban.csv"
OUTPUT_PATH = "../processed/facilities_health.csv"

df = pd.read_csv(INPUT_PATH)

# Build a full address string per row for geocoding.
# Fall back gracefully if street name is missing.
def build_address(row):
    parts = []
    if pd.notna(row.get("Street Name and #")) and str(row["Street Name and #"]).strip():
        parts.append(str(row["Street Name and #"]).strip())
    parts.append(str(row["Barangay Name"]).strip())
    parts.append(str(row["City/Municipality Name"]).strip())
    parts.append(str(row["Province Name"]).strip())
    parts.append("Philippines")
    return ", ".join(parts)

df["full_address"] = df.apply(build_address, axis=1)

geolocator = Nominatim(user_agent="lingap_facility_geocoder")
# Nominatim's usage policy requires max 1 request/sec
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)

def try_geocode(address, barangay, fallback_muni="Rodriguez, Rizal, Philippines"):
    """Try full address first; fall back to barangay-level if it fails."""
    location = geocode(address)
    if location:
        return location.latitude, location.longitude, "address_level"
    # fallback: just barangay + municipality (less precise but still usable)
    fallback_address = f"{barangay}, {fallback_muni}"
    location = geocode(fallback_address)
    if location:
        return location.latitude, location.longitude, "barangay_level"
    return None, None, "failed"

print(f"Geocoding {len(df)} facilities... this will take a few minutes (rate limited).")

lats, lngs, precisions = [], [], []
for i, row in df.iterrows():
    lat, lng, precision = try_geocode(row["full_address"], row["Barangay Name"])
    lats.append(lat)
    lngs.append(lng)
    precisions.append(precision)
    print(f"[{i+1}/{len(df)}] {row['Facility Name'][:50]:50s} -> {precision}")

df["lat"] = lats
df["lng"] = lngs
df["geocode_precision"] = precisions

# Build cleaned output matching your `facilities` table columns
output = pd.DataFrame({
    "facility_name": df["Facility Name"],
    "facility_type": df["Health Facility Type"].apply(
        lambda x: "health"  # all rows in this file are health facilities
    ),
    "facility_subtype": df["Health Facility Type"],  # keep detail (RHU, BHS, Hospital, etc.)
    "barangay": df["Barangay Name"],
    "barangay_psgc": df["Barangay PSGC"],
    "address": df["full_address"],
    "lat": df["lat"],
    "lng": df["lng"],
    "geocode_precision": df["geocode_precision"],
    "ownership": df["Ownership Major Classification"],
    "bed_capacity": df["Bed Capacity"],
})

output.to_csv(OUTPUT_PATH, index=False)
print(f"\nDone. Saved to {OUTPUT_PATH}")
print(f"Geocoded: {df['lat'].notna().sum()} / {len(df)}")
print(f"Failed: {df['lat'].isna().sum()}")

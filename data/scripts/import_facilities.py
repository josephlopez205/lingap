"""
Import health facilities and schools into the facilities table,
keyed to barangay_id via barangay name lookup.

Fix: normalize barangay names (strip + uppercase) on both the DB lookup side
and the CSV side before matching, to avoid silent skips from whitespace/casing
mismatches (same issue found in import_demographics.py).
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv("../../backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

health = pd.read_csv("../processed/facilities_health.csv")
schools = pd.read_csv("../processed/facilities_schools.csv")

print(f"Loaded {len(health)} health facilities, {len(schools)} schools")

with engine.begin() as conn:
    # Build normalized barangay name -> barangay_id lookup
    result = conn.execute(text("SELECT barangay_id, name FROM barangays"))
    lookup = {row.name.strip().upper(): row.barangay_id for row in result}

    def resolve_barangay(name):
        if pd.isna(name):
            return None
        return lookup.get(str(name).strip().upper())

    inserted, skipped = 0, 0
    skipped_rows = []

    # --- Health facilities ---
    for _, row in health.iterrows():
        barangay_id = resolve_barangay(row.get("barangay"))
        if not barangay_id:
            skipped += 1
            skipped_rows.append(("health", row["facility_name"], row.get("barangay")))
            continue

        conn.execute(
            text("""
                INSERT INTO facilities
                    (barangay_id, facility_name, facility_type, geom, source)
                VALUES
                    (:barangay_id, :name, 'health', ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :source)
            """),
            {
                "barangay_id": barangay_id,
                "name": row["facility_name"],
                "lat": row["lat"],
                "lng": row["lng"],
                "source": f"DOH NHFR ({row.get('geocode_precision', 'unknown precision')})",
            }
        )
        inserted += 1

    # --- Schools ---
    for _, row in schools.iterrows():
        barangay_id = resolve_barangay(row.get("barangay"))
        if not barangay_id:
            skipped += 1
            skipped_rows.append(("school", row["facility_name"], row.get("barangay")))
            continue

        conn.execute(
            text("""
                INSERT INTO facilities
                    (barangay_id, facility_name, facility_type, geom, source)
                VALUES
                    (:barangay_id, :name, 'school', ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :source)
            """),
            {
                "barangay_id": barangay_id,
                "name": row["facility_name"],
                "lat": row["lat"],
                "lng": row["lng"],
                "source": f"DepEd SDO Rizal ({row.get('geocode_precision', 'unknown precision')})",
            }
        )
        inserted += 1

print(f"\nInserted {inserted} facility rows, skipped {skipped} (no barangay match).")

if skipped_rows:
    print("\nSkipped rows (no matching barangay found):")
    for kind, name, barangay in skipped_rows:
        print(f"  [{kind}] {name!r} — barangay value was: {barangay!r}")

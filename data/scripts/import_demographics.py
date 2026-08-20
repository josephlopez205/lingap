"""
Import demographics (population figures) into Postgres, keyed to barangay_id
via barangay name lookup.
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv("../../backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

df = pd.read_csv("../processed/rodriguez_barangays.csv")
print(f"Loaded {len(df)} demographic rows")

with engine.begin() as conn:
    # Build barangay name -> barangay_id lookup, normalized for matching
    result = conn.execute(text("SELECT barangay_id, name FROM barangays"))
    lookup = {row.name.strip().upper(): row.barangay_id for row in result}

    inserted, skipped = 0, 0
    for _, row in df.iterrows():
        clean_name = str(row["barangay_name"]).strip().upper()
        barangay_id = lookup.get(clean_name)
        if not barangay_id:
            print(f" No matching barangay_id for '{row['barangay_name']}' — skipping")
            skipped += 1
            continue

        conn.execute(
            text("""
                INSERT INTO demographics
                    (barangay_id, population_total, poverty_incidence_pct, source)
                VALUES
                    (:barangay_id, :population_total, :poverty_pct, :source)
                ON CONFLICT (barangay_id) DO UPDATE SET
                    population_total = EXCLUDED.population_total,
                    source = EXCLUDED.source,
                    updated_at = now()
            """),
            {
                "barangay_id": barangay_id,
                "population_total": int(row["population_2024"]),
                "poverty_pct": None,  # not available in this source — left NULL, not synthesized
                "source": "PSA PSGC 2Q2026 / 2024 POPCEN",
            }
        )
        inserted += 1

print(f"\nInserted/updated {inserted} demographic rows, skipped {skipped}.")

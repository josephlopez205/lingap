"""
Import Rodriguez barangay boundaries (geometry) + master names/PSGC codes into Postgres.
Combines rodriguez_barangays.geojson (geometry) with rodriguez_barangays.csv (names, PSGC, population)
via the adm4_name field matched against the barangay_name column.

Fix: normalize both sides (strip + uppercase) before merging to eliminate
whitespace/casing mismatches that caused silent unmatched rows (e.g. "Balite").
"""

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv("../../backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

LGU_NAME = "Rodriguez"
LGU_PROVINCE = "Rizal"
LGU_REGION = "Region IV-A (CALABARZON)"
LGU_INCOME_CLASS = "1st"

# --- Step 1: Insert the LGU row (only once) ---
with engine.begin() as conn:
    existing = conn.execute(
        text("SELECT lgu_id FROM lgus WHERE name = :name"), {"name": LGU_NAME}
    ).fetchone()

    if existing:
        lgu_id = existing[0]
        print(f"LGU '{LGU_NAME}' already exists with lgu_id={lgu_id}")
    else:
        result = conn.execute(
            text("""
                INSERT INTO lgus (name, province, region, income_classification)
                VALUES (:name, :province, :region, :income_class)
                RETURNING lgu_id
            """),
            {"name": LGU_NAME, "province": LGU_PROVINCE, "region": LGU_REGION, "income_class": LGU_INCOME_CLASS}
        )
        lgu_id = result.fetchone()[0]
        print(f"Inserted LGU '{LGU_NAME}' with lgu_id={lgu_id}")

# --- Step 2: Load boundary geometries ---
gdf = gpd.read_file("../processed/rodriguez_barangays.geojson")
print(f"Loaded {len(gdf)} boundary features")

# Clean + normalize barangay name: strip "(Pob.)"-style suffixes, whitespace, casing
gdf["clean_name"] = (
    gdf["adm4_name"]
    .str.replace(r"\s*\(.*?\)\s*", "", regex=True)
    .str.strip()
    .str.upper()
)

# --- Step 3: Load names/PSGC/population master CSV ---
master = pd.read_csv("../processed/rodriguez_barangays.csv")
print(f"Loaded {len(master)} master rows")

# Normalize the CSV side the same way
master["barangay_name_clean"] = master["barangay_name"].str.strip().str.upper()

# --- Step 4: Merge on normalized barangay name ---
merged = gdf.merge(
    master, left_on="clean_name", right_on="barangay_name_clean", how="left", indicator=True
)

unmatched = merged[merged["_merge"] != "both"]
if len(unmatched) > 0:
    print("\n WARNING: unmatched rows (name mismatch between geojson and CSV):")
    print(unmatched[["adm4_name", "clean_name"]])
else:
    print("All boundary features matched to master CSV rows.")

# --- Step 5: Insert into barangays table ---
with engine.begin() as conn:
    for _, row in merged.iterrows():
        # Display-friendly name: Title Case (e.g. "BALITE" -> "Balite")
        display_name = row["clean_name"].title()

        conn.execute(
            text("""
                INSERT INTO barangays (lgu_id, name, psgc_code, geom, source)
                VALUES (:lgu_id, :name, :psgc_code, ST_GeomFromText(:wkt, 4326), :source)
            """),
            {
                "lgu_id": lgu_id,
                "name": display_name,
                "psgc_code": str(row.get("psgc_code", "")) if pd.notna(row.get("psgc_code")) else None,
                "wkt": row.geometry.wkt,
                "source": "PhilGIS/HDX boundary + PSA PSGC 2Q2026",
            }
        )

print(f"\nInserted {len(merged)} barangay rows.")

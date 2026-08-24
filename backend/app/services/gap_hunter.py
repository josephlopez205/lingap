# Distance calculations use PostGIS ST_Distance() directly in SQL (see queries below).
# See services/geo_utils.py for an independent Haversine reference/testing implementation.
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

# Thresholds confirmed against real Rodriguez, Rizal centroid-distance data (see docs/gap-hunter-rules.md)
HEALTH_POPULATION_THRESHOLD = 3000
HEALTH_DISTANCE_THRESHOLD_KM = 3.0
EDUCATION_POPULATION_THRESHOLD = 3000
EDUCATION_DISTANCE_THRESHOLD_KM = 3.0


def run_facility_access_rule(db: Session, lgu_id: int, facility_type: str,
                              sector: str, rule_id: str,
                              population_threshold: int, distance_threshold_km: float):
    """
    Flags barangays where population exceeds threshold AND the nearest facility
    of the given type (measured from barangay CENTROID, not polygon edge —
    fixes the zero-distance bug for facilities located within their own barangay)
    exceeds the distance threshold.
    """
    rows = db.execute(
        text("""
            WITH nearest_facility AS (
                SELECT b.barangay_id,
                       b.name,
                       d.population_total,
                       MIN(ST_Distance(ST_Centroid(b.geom)::geography, f.geom::geography)) / 1000 AS nearest_km,
                       ST_X(ST_Centroid(b.geom)) AS centroid_lng,
                       ST_Y(ST_Centroid(b.geom)) AS centroid_lat
                FROM barangays b
                LEFT JOIN demographics d ON b.barangay_id = d.barangay_id
                LEFT JOIN facilities f ON f.facility_type = :facility_type
                WHERE b.lgu_id = :lgu_id
                GROUP BY b.barangay_id, b.name, d.population_total, b.geom
            )
            SELECT barangay_id, name, population_total, nearest_km, centroid_lng, centroid_lat
            FROM nearest_facility
            WHERE population_total > :pop_threshold
              AND (nearest_km > :dist_threshold OR nearest_km IS NULL)
        """),
        {
            "lgu_id": lgu_id,
            "facility_type": facility_type,
            "pop_threshold": population_threshold,
            "dist_threshold": distance_threshold_km,
        }
    ).fetchall()

    gaps = []
    for row in rows:
        gaps.append({
            "lgu_id": lgu_id,
            "barangay_id": row.barangay_id,
            "sector": sector,
            "rule_id": rule_id,
            "affected_population": row.population_total,
            "evidence_data": {
                "population_total": row.population_total,
                "nearest_facility_km": round(row.nearest_km, 2) if row.nearest_km is not None else None,
                "population_threshold": population_threshold,
                "distance_threshold_km": distance_threshold_km,
            },
            "centroid_lat": row.centroid_lat,
            "centroid_lng": row.centroid_lng,
        })
    return gaps


def compute_severity_score(gap, max_population_in_lgu):
    """
    severity = (0.6 x normalized population affected) + (0.4 x normalized distance deficit)
    Poverty weighting term dropped — no barangay-level poverty data available (see docs/gap-hunter-rules.md).
    """
    pop_component = (gap["affected_population"] / max_population_in_lgu) * 100 if max_population_in_lgu else 0

    distance = gap["evidence_data"].get("nearest_facility_km") or 0
    threshold = gap["evidence_data"].get("distance_threshold_km", 1)
    deficit_ratio = min(distance / threshold, 3)
    deficit_component = (deficit_ratio / 3) * 100

    score = (0.6 * pop_component) + (0.4 * deficit_component)
    return round(min(score, 100), 1)


def run_gap_hunter(db: Session, lgu_id: int):
    db.execute(text("DELETE FROM gaps WHERE lgu_id = :lgu_id"), {"lgu_id": lgu_id})

    all_gaps = []

    all_gaps += run_facility_access_rule(
        db, lgu_id, facility_type="health", sector="Health", rule_id="HEALTH_ACCESS_POPULATION",
        population_threshold=HEALTH_POPULATION_THRESHOLD, distance_threshold_km=HEALTH_DISTANCE_THRESHOLD_KM,
    )

    all_gaps += run_facility_access_rule(
        db, lgu_id, facility_type="school", sector="Education", rule_id="EDU_ACCESS_POPULATION",
        population_threshold=EDUCATION_POPULATION_THRESHOLD, distance_threshold_km=EDUCATION_DISTANCE_THRESHOLD_KM,
    )

    if not all_gaps:
        db.commit()
        return 0

    max_population = max(g["affected_population"] for g in all_gaps)

    for gap in all_gaps:
        gap["severity_score"] = compute_severity_score(gap, max_population)
        db.execute(
            text("""
                INSERT INTO gaps
                    (lgu_id, barangay_id, sector, rule_id, severity_score,
                     affected_population, evidence_data, centroid_lat, centroid_lng)
                VALUES
                    (:lgu_id, :barangay_id, :sector, :rule_id, :severity_score,
                     :affected_population, :evidence_data, :centroid_lat, :centroid_lng)
            """),
            {**gap, "evidence_data": json.dumps(gap["evidence_data"])}
        )

    db.commit()
    return len(all_gaps)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import get_db

router = APIRouter(prefix="/api/barangay", tags=["barangay"])


@router.get("/{barangay_id}/detail")
def get_barangay_detail(barangay_id: int, db: Session = Depends(get_db)):
    # 1. Fetch barangay + demographics
    row = db.execute(
        text("""
            SELECT b.name, d.population_total, d.population_0_14, d.population_15_59,
                   d.population_60_plus, d.poverty_incidence_pct
            FROM barangays b
            LEFT JOIN demographics d ON b.barangay_id = d.barangay_id
            WHERE b.barangay_id = :barangay_id
        """),
        {"barangay_id": barangay_id}
    ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Barangay {barangay_id} not found")

    # 2. Fetch facility counts
    counts = db.execute(
        text("""
            SELECT
              (SELECT count(*) FROM facilities WHERE barangay_id = :barangay_id AND facility_type = 'health') as health_count,
              (SELECT count(*) FROM facilities WHERE barangay_id = :barangay_id AND facility_type = 'school') as school_count
        """),
        {"barangay_id": barangay_id}
    ).fetchone()

    # 3. Assemble response
    return {
        "name": row.name,
        "population_total": row.population_total,
        "population_0_14": row.population_0_14,
        "population_15_59": row.population_15_59,
        "population_60_plus": row.population_60_plus,
        "poverty_incidence_pct": float(row.poverty_incidence_pct) if row.poverty_incidence_pct is not None else None,
        "health_facility_count": counts.health_count,
        "school_count": counts.school_count,
        "active_gap_count": 0  # hardcoded — GAP Hunter engine is Phase 3
    }

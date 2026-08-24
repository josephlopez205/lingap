from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import get_db
from app.services.gap_hunter import run_gap_hunter

router = APIRouter(prefix="/api", tags=["gaps"])


@router.post("/lgu/{lgu_id}/gaps/analyze")
def analyze_gaps(lgu_id: int, db: Session = Depends(get_db)):
    count = run_gap_hunter(db, lgu_id)
    return {"gaps_found": count}


@router.get("/lgu/{lgu_id}/gaps")
def get_gaps(lgu_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT g.gap_id, g.barangay_id, b.name as barangay_name, g.sector, g.rule_id,
                   g.severity_score, g.affected_population, g.evidence_data,
                   g.centroid_lat, g.centroid_lng
            FROM gaps g
            JOIN barangays b ON g.barangay_id = b.barangay_id
            WHERE g.lgu_id = :lgu_id AND g.status = 'active'
            ORDER BY g.severity_score DESC
        """),
        {"lgu_id": lgu_id}
    ).fetchall()

    return [
        {
            "gap_id": r.gap_id,
            "barangay_id": r.barangay_id,
            "barangay_name": r.barangay_name,
            "sector": r.sector,
            "rule_id": r.rule_id,
            "severity_score": float(r.severity_score),
            "affected_population": r.affected_population,
            "evidence_data": r.evidence_data,
            "centroid_lat": float(r.centroid_lat),
            "centroid_lng": float(r.centroid_lng),
        }
        for r in rows
    ]

# backend/app/routers/lgu.py

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import get_db

router = APIRouter(prefix="/api/lgu", tags=["lgu"])

@router.get("/{lgu_id}/boundaries")
def get_lgu_boundaries(lgu_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT b.barangay_id, b.name, ST_AsGeoJSON(b.geom) as geom,
                   d.population_total, d.poverty_incidence_pct
            FROM barangays b
            LEFT JOIN demographics d ON b.barangay_id = d.barangay_id
            WHERE b.lgu_id = :lgu_id
        """),
        {"lgu_id": lgu_id}
    ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No barangays found for lgu_id={lgu_id}")

    features = []
    for row in rows:
        features.append({
            "type": "Feature",
            "properties": {
                "barangay_id": row.barangay_id,
                "name": row.name,
                "population_total": row.population_total,
                "poverty_incidence_pct": float(row.poverty_incidence_pct) if row.poverty_incidence_pct is not None else None,
            },
            "geometry": json.loads(row.geom)
        })

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    bbox_row = db.execute(
        text("""
            SELECT ST_XMin(ST_Extent(geom)) as min_lng,
                   ST_YMin(ST_Extent(geom)) as min_lat,
                   ST_XMax(ST_Extent(geom)) as max_lng,
                   ST_YMax(ST_Extent(geom)) as max_lat
            FROM barangays
            WHERE lgu_id = :lgu_id
        """),
        {"lgu_id": lgu_id}
    ).fetchone()

    bbox = {
        "min_lng": bbox_row.min_lng,
        "min_lat": bbox_row.min_lat,
        "max_lng": bbox_row.max_lng,
        "max_lat": bbox_row.max_lat
    }

    return {
        **feature_collection,
        "bbox": bbox
    }

@router.get("/{lgu_id}/facilities")
def get_lgu_facilities(lgu_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT f.facility_id, f.facility_name, f.facility_type, f.capacity, f.barangay_id,
                   ST_AsGeoJSON(f.geom) as geom
            FROM facilities f
            JOIN barangays b ON f.barangay_id = b.barangay_id
            WHERE b.lgu_id = :lgu_id
        """),
        {"lgu_id": lgu_id}
    ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No facilities found for lgu_id={lgu_id}")

    features = []
    for row in rows:
        features.append({
            "type": "Feature",
            "properties": {
                "facility_id": row.facility_id,
                "facility_name": row.facility_name,
                "facility_type": row.facility_type,
                "capacity": row.capacity,
                "barangay_id": row.barangay_id
            },
            "geometry": json.loads(row.geom)
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

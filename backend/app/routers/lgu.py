# backend/app/routers/lgu.py

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import get_db

router = APIRouter(prefix="/api/lgu", tags=["lgu"])


@router.get("/{lgu_id}/boundaries")
def get_lgu_boundaries(lgu_id: int, db: Session = Depends(get_db)):
    # 1. Fetch barangay geometries
    rows = db.execute(
        text("""
            SELECT barangay_id, name, ST_AsGeoJSON(geom) as geom
            FROM barangays
            WHERE lgu_id = :lgu_id
        """),
        {"lgu_id": lgu_id}
    ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No barangays found for lgu_id={lgu_id}")

    # 2. Assemble FeatureCollection
    features = []
    for row in rows:
        features.append({
            "type": "Feature",
            "properties": {
                "barangay_id": row.barangay_id,
                "name": row.name
            },
            "geometry": json.loads(row.geom)  # geom comes back as a JSON string, parse it
        })

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    # 3. Compute bounding box
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

    # 4. Return combined response
    return {
        **feature_collection,
        "bbox": bbox
    }

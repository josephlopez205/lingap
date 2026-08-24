# backend/app/services/geo_utils.py
"""
Haversine distance helper — kept as a reference/fallback implementation.

NOTE: The live GAP Hunter engine (gap_hunter.py) does NOT use this function.
It computes distance directly in SQL via PostGIS's ST_Distance(geography),
which is faster (avoids pulling every coordinate pair into Python) and more
accurate (accounts for Earth's ellipsoid shape via the geography type, rather
than treating Earth as a perfect sphere like Haversine does).

This function is kept for:
  - Unit testing the SQL distance logic against an independent calculation
  - Any future case where distance needs computing outside the database
    (e.g., in a script that doesn't have a live DB connection)
"""
from math import radians, sin, cos, sqrt, atan2


def haversine_km(lat1, lng1, lat2, lng2):
    """Calculate great-circle distance in km between two lat/lng points."""
    R = 6371  # Earth's mean radius in km
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

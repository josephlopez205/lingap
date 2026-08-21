"""
Smoke test for Phase 2 endpoints.
Run with the server already up: uvicorn app.main:app --port 8000
"""
import requests
import sys

BASE_URL = "http://localhost:8000"
LGU_ID = 1
TEST_BARANGAY_ID = 1   # pick one you know exists

failures = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not condition:
        failures.append(name)


def test_boundaries():
    print("\n--- /api/lgu/{lgu_id}/boundaries ---")
    r = requests.get(f"{BASE_URL}/api/lgu/{LGU_ID}/boundaries")
    check("Status 200", r.status_code == 200, f"(got {r.status_code})")
    if r.status_code != 200:
        return
    data = r.json()
    check("Has type=FeatureCollection", data.get("type") == "FeatureCollection")
    check("Has non-empty features list", len(data.get("features", [])) > 0,
          f"(count={len(data.get('features', []))})")
    check("Has bbox", "bbox" in data)
    if "bbox" in data:
        bbox = data["bbox"]
        check("bbox has all 4 fields, no None", all(
            bbox.get(k) is not None for k in ["min_lng", "min_lat", "max_lng", "max_lat"]
        ))
        # Sanity range check for Philippines
        check("bbox lng in PH range (117-127)", 117 <= bbox["min_lng"] <= 127 and 117 <= bbox["max_lng"] <= 127,
              f"(min_lng={bbox.get('min_lng')}, max_lng={bbox.get('max_lng')})")
        check("bbox lat in PH range (4-21)", 4 <= bbox["min_lat"] <= 21 and 4 <= bbox["max_lat"] <= 21,
              f"(min_lat={bbox.get('min_lat')}, max_lat={bbox.get('max_lat')})")
    if data.get("features"):
        f0 = data["features"][0]
        check("Feature has barangay_id + name", "barangay_id" in f0["properties"] and "name" in f0["properties"])
        check("Feature geometry is Polygon/MultiPolygon", f0["geometry"]["type"] in ("Polygon", "MultiPolygon"))
    # 404 path
    r404 = requests.get(f"{BASE_URL}/api/lgu/999999/boundaries")
    check("Unknown lgu_id returns 404", r404.status_code == 404)


def test_facilities():
    print("\n--- /api/lgu/{lgu_id}/facilities ---")
    r = requests.get(f"{BASE_URL}/api/lgu/{LGU_ID}/facilities")
    check("Status 200", r.status_code == 200, f"(got {r.status_code})")
    if r.status_code != 200:
        return
    data = r.json()
    check("Has type=FeatureCollection", data.get("type") == "FeatureCollection")
    features = data.get("features", [])
    check("Has non-empty features list", len(features) > 0, f"(count={len(features)})")
    if features:
        f0 = features[0]
        props = f0["properties"]
        check("Feature has all required properties",
              all(k in props for k in ["facility_name", "facility_type", "capacity", "barangay_id"]))
        check("facility_type is 'health' or 'school'", props["facility_type"] in ("health", "school"),
              f"(got {props['facility_type']!r})")
        check("Geometry is Point", f0["geometry"]["type"] == "Point")
        lng, lat = f0["geometry"]["coordinates"]
        check("No NaN in coordinates", lng == lng and lat == lat)  # NaN != NaN trick
        check("Coordinates in PH range", 117 <= lng <= 127 and 4 <= lat <= 21,
              f"(lng={lng}, lat={lat})")
    # check no duplicate (facility_name, barangay_id) pairs
    seen = set()
    dupes = 0
    for f in features:
        key = (f["properties"]["facility_name"], f["properties"]["barangay_id"])
        if key in seen:
            dupes += 1
        seen.add(key)
    check("No duplicate facilities", dupes == 0, f"(found {dupes} duplicates)")


def test_barangay_detail():
    print("\n--- /api/barangay/{barangay_id}/detail ---")
    r = requests.get(f"{BASE_URL}/api/barangay/{TEST_BARANGAY_ID}/detail")
    check("Status 200", r.status_code == 200, f"(got {r.status_code})")
    if r.status_code != 200:
        return
    data = r.json()
    required_fields = [
        "name", "population_total", "population_0_14", "population_15_59",
        "population_60_plus", "poverty_incidence_pct",
        "health_facility_count", "school_count", "active_gap_count"
    ]
    check("Has all 9 required fields", all(k in data for k in required_fields),
          f"(missing: {[k for k in required_fields if k not in data]})")
    check("active_gap_count is 0 (placeholder)", data.get("active_gap_count") == 0)
    check("health_facility_count is int >= 0", isinstance(data.get("health_facility_count"), int) and data["health_facility_count"] >= 0)
    check("school_count is int >= 0", isinstance(data.get("school_count"), int) and data["school_count"] >= 0)
    # 404 path
    r404 = requests.get(f"{BASE_URL}/api/barangay/999999/detail")
    check("Unknown barangay_id returns 404", r404.status_code == 404)


def cross_check_counts():
    print("\n--- Cross-check: facility counts match between endpoints ---")
    fac_r = requests.get(f"{BASE_URL}/api/lgu/{LGU_ID}/facilities")
    detail_r = requests.get(f"{BASE_URL}/api/barangay/{TEST_BARANGAY_ID}/detail")
    if fac_r.status_code != 200 or detail_r.status_code != 200:
        check("Cross-check skipped (dependent call failed)", False)
        return
    features = fac_r.json()["features"]
    health_count = sum(1 for f in features
                        if f["properties"]["barangay_id"] == TEST_BARANGAY_ID
                        and f["properties"]["facility_type"] == "health")
    school_count = sum(1 for f in features
                        if f["properties"]["barangay_id"] == TEST_BARANGAY_ID
                        and f["properties"]["facility_type"] == "school")
    detail = detail_r.json()
    check("health_facility_count matches raw facilities data",
          detail["health_facility_count"] == health_count,
          f"(detail={detail['health_facility_count']}, actual={health_count})")
    check("school_count matches raw facilities data",
          detail["school_count"] == school_count,
          f"(detail={detail['school_count']}, actual={school_count})")


if __name__ == "__main__":
    test_boundaries()
    test_facilities()
    test_barangay_detail()
    cross_check_counts()

    print("\n" + "=" * 50)
    if failures:
        print(f"❌ {len(failures)} CHECK(S) FAILED:")
        for f in failures:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("✅ ALL CHECKS PASSED — safe for frontend to begin.")
        sys.exit(0)

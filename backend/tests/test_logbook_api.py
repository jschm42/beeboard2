from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.apiary import Apiary

def test_logbook_session_renaming_and_validation(client: TestClient, db: Session):
    # 1. Register and login
    reg_response = client.post("/api/auth/register", json={
        "username": "sessiontester",
        "email": "sessiontester@example.com",
        "password": "strongpassword123",
        "first_name": "Session",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "sessiontester",
        "password": "strongpassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create an apiary for testing
    apiary_resp = client.post("/api/apiaries", json={
        "name": "Test Apiary",
        "address": "Honey Lane 1"
    }, headers=headers)
    assert apiary_resp.status_code == 201
    apiary_id = apiary_resp.json()["id"]
    
    # 3. Create a logbook session
    session_resp = client.post(f"/api/logbook/sessions?apiary_id={apiary_id}", json={
        "title": "Short Title",
        "hive_id": None
    }, headers=headers)
    assert session_resp.status_code == 201
    session_data = session_resp.json()
    assert session_data["title"] == "Short Title"
    session_id = session_data["id"]
    
    # 4. Rename the session successfully (30 chars or less)
    rename_resp = client.put(f"/api/logbook/sessions/{session_id}", json={
        "title": "Exactly Thirty Characters Long!", # 31? Let's check: "Exactly Thirty Characters Long!" has 31 characters.
        "hive_id": None
    }, headers=headers)
    # Let's count "Exactly Thirty Characters Long" = 30 chars.
    rename_resp = client.put(f"/api/logbook/sessions/{session_id}", json={
        "title": "Exactly Thirty Characters Long",
        "hive_id": None
    }, headers=headers)
    assert rename_resp.status_code == 200
    assert rename_resp.json()["title"] == "Exactly Thirty Characters Long"
    
    # 5. Rename session fails when exceeding 30 characters
    rename_fail_resp = client.put(f"/api/logbook/sessions/{session_id}", json={
        "title": "This is a title that exceeds thirty characters by quite a bit",
        "hive_id": None
    }, headers=headers)
    assert rename_fail_resp.status_code == 422
    assert "value_error.any_str.max_length" in str(rename_fail_resp.json()["detail"]) or "string_too_long" in str(rename_fail_resp.json()["detail"])

    # 6. Create scoped sessions (APIARY, LOCATION, HIVE) and test list query
    # Retrieve default frame type first
    ft_resp = client.get("/api/hives/frame-types", headers=headers)
    zander_ft = ft_resp.json()[0]

    # Create location
    loc_resp = client.post(f"/api/locations?apiary_id={apiary_id}", json={
        "name": "Test Location",
        "address": "Testweg 1"
    }, headers=headers)
    assert loc_resp.status_code == 201
    loc_id = loc_resp.json()["id"]

    # Create hive
    hive_resp = client.post(f"/api/hives?apiary_id={apiary_id}", json={
        "name": "Test Hive",
        "location_id": loc_id,
        "frame_type_id": zander_ft["id"],
        "queen_year": 2026,
        "is_active": True
    }, headers=headers)
    assert hive_resp.status_code == 201
    hive_id = hive_resp.json()["id"]

    # Create Hive scoped session
    hive_session_resp = client.post(f"/api/logbook/sessions?apiary_id={apiary_id}", json={
        "title": "Hive Session",
        "scope_type": "HIVE",
        "linked_hive_ids": [hive_id]
    }, headers=headers)
    assert hive_session_resp.status_code == 201
    hive_session_data = hive_session_resp.json()
    assert hive_session_data["scope_type"] == "HIVE"
    assert len(hive_session_data["linked_hives"]) == 1
    assert hive_session_data["linked_hives"][0]["id"] == hive_id

    # Create Location scoped session
    loc_session_resp = client.post(f"/api/logbook/sessions?apiary_id={apiary_id}", json={
        "title": "Location Session",
        "scope_type": "LOCATION",
        "linked_location_ids": [loc_id]
    }, headers=headers)
    assert loc_session_resp.status_code == 201
    loc_session_data = loc_session_resp.json()
    assert loc_session_data["scope_type"] == "LOCATION"
    assert len(loc_session_data["linked_locations"]) == 1
    assert loc_session_data["linked_locations"][0]["id"] == loc_id


def test_logbook_box_creation_and_stats(client: TestClient, db: Session):
    # 1. Register and login
    reg_response = client.post("/api/auth/register", json={
        "username": "snapshotter",
        "email": "snapshotter@example.com",
        "password": "strongpassword123",
        "first_name": "Snapshot",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "snapshotter",
        "password": "strongpassword123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create an apiary and location
    apiary_resp = client.post("/api/apiaries", json={
        "name": "Snapshot Apiary",
        "address": "Honey Road 2"
    }, headers=headers)
    apiary_id = apiary_resp.json()["id"]
    
    loc_resp = client.post(f"/api/locations?apiary_id={apiary_id}", json={
        "name": "Standschnitt",
        "address": "Forstwald 12"
    }, headers=headers)
    loc_id = loc_resp.json()["id"]
    
    # 3. Retrieve available FrameTypes
    ft_resp = client.get("/api/hives/frame-types", headers=headers)
    frame_types = ft_resp.json()
    zander_ft = next(f for f in frame_types if f["name"] == "Zander")
    
    # 4. Create a hive with Zander default frame type
    hive_resp = client.post(f"/api/hives?apiary_id={apiary_id}", json={
        "name": "Snapshot Hive",
        "location_id": loc_id,
        "frame_type_id": zander_ft["id"],
        "queen_year": 2026,
        "is_active": True,
        "notes": "Testing snapshotted factors"
    }, headers=headers)
    hive_id = hive_resp.json()["id"]
    
    # 5. Configure 1 box with Zander frame type
    boxes_resp = client.post(f"/api/hives/{hive_id}/boxes", json=[{
        "order": 1,
        "frame_type_id": zander_ft["id"],
        "frame_count": 10,
        "box_type": "BROOD"
    }], headers=headers)
    assert boxes_resp.status_code == 200
    
    # 6. Create an Inspection Log Entry (INSPECTION)
    entry_resp = client.post(f"/api/logbook/entries?apiary_id={apiary_id}", json={
        "hive_id": hive_id,
        "session_id": None,
        "date": "2026-05-18",
        "entry_type": "INSPECTION",
        "notes": "Testing multipliers",
        "inspection_detail": {
            "boxes": [
                {
                    "box_index": 0,
                    "brood_eighths": 4,
                    "food_eighths": 2,
                    "bee_eighths": 6,
                    "drone_eighths": 1,
                    "drone_brood_eighths": 0,
                    "pollen_eighths": 2
                }
            ]
        }
    }, headers=headers)
    assert entry_resp.status_code == 201
    entry_data = entry_resp.json()
    assert len(entry_data["inspection_detail"]["boxes"]) == 1
    
    # 7. Check stats aggregation returns correct calculations
    stats_resp = client.get(f"/api/stats/aggregation?apiary_id={apiary_id}", headers=headers)
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert len(stats_data["labels"]) == 1
    
    # Zander factors are: brood=400, food=125, bees=125
    # 4 eighths brood * 400 = 1600.0
    # 2 eighths food * 125 = 250.0
    # 6 eighths bees * 125 = 750.0
    assert stats_data["brood"][0] == 1600.0
    assert stats_data["food"][0] == 250.0
    assert stats_data["bees"][0] == 750.0


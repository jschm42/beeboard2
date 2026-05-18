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

def test_logbook_multiplier_snapshotting(client: TestClient, db: Session):
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
    langstroth_ft = next(f for f in frame_types if f["name"] == "Langstroth")
    
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
    
    # 5. Configure 1 box with Langstroth frame type
    boxes_resp = client.post(f"/api/hives/{hive_id}/boxes", json=[{
        "order": 1,
        "frame_type_id": langstroth_ft["id"],
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
            "frames": [
                {
                    "frame_number": 1,
                    "side": 1,
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
    
    # Assert snapshotted multipliers on the frame match Langstroth multipliers, not Zander!
    frame = entry_data["inspection_detail"]["frames"][0]
    assert frame["brood_multiplier"] == float(langstroth_ft["brood_multiplier"])
    assert frame["food_multiplier"] == float(langstroth_ft["food_multiplier"])
    assert frame["bee_multiplier"] == float(langstroth_ft["bee_multiplier"])
    assert frame["drone_multiplier"] == float(langstroth_ft["drone_multiplier"])
    assert frame["drone_brood_multiplier"] == float(langstroth_ft["drone_brood_multiplier"])
    assert frame["pollen_multiplier"] == float(langstroth_ft["pollen_multiplier"])
    
    # 7. Reconfigure the box to Zander frame type
    boxes_resp2 = client.post(f"/api/hives/{hive_id}/boxes", json=[{
        "order": 1,
        "frame_type_id": zander_ft["id"],
        "frame_count": 10,
        "box_type": "BROOD"
    }], headers=headers)
    assert boxes_resp2.status_code == 200
    
    # 8. Retrieve the historical log entry and assert multipliers remain snapshotted as Langstroth!
    entries_resp = client.get(f"/api/logbook/entries?apiary_id={apiary_id}", headers=headers)
    historical_entry = entries_resp.json()[0]
    hist_frame = historical_entry["inspection_detail"]["frames"][0]
    
    # Verify they did NOT change to Zander multipliers!
    assert hist_frame["brood_multiplier"] == float(langstroth_ft["brood_multiplier"])
    assert hist_frame["food_multiplier"] == float(langstroth_ft["food_multiplier"])
    assert hist_frame["bee_multiplier"] == float(langstroth_ft["bee_multiplier"])


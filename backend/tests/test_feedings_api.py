from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date


def test_feed_types_and_feedings_workflow(client: TestClient, db: Session):
    # 1. Register and login admin user
    reg_response = client.post("/api/auth/register", json={
        "username": "feedingadmin",
        "email": "feedingadmin@example.com",
        "password": "strongpassword123",
        "first_name": "Admin",
        "last_name": "Feeding"
    })
    assert reg_response.status_code == 201

    login_response = client.post("/api/auth/login", data={
        "username": "feedingadmin",
        "password": "strongpassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {token}"}

    # 2. Register and login normal user
    reg_response2 = client.post("/api/auth/register", json={
        "username": "feedinguser",
        "email": "feedinguser@example.com",
        "password": "strongpassword123",
        "first_name": "Normal",
        "last_name": "Feeding"
    })
    assert reg_response2.status_code == 201

    login_response2 = client.post("/api/auth/login", data={
        "username": "feedinguser",
        "password": "strongpassword123"
    })
    assert login_response2.status_code == 200
    token2 = login_response2.json()["access_token"]
    normal_headers = {"Authorization": f"Bearer {token2}"}

    # 3. Test Admin Feed Types
    # List feed types (initial seeded ones)
    ft_resp = client.get("/api/admin/feed-types", headers=admin_headers)
    assert ft_resp.status_code == 200
    initial_fts = ft_resp.json()
    assert len(initial_fts) >= 4

    # Create new feed type as Admin
    new_ft_resp = client.post("/api/admin/feed-types", json={
        "name": "Bio-Invertzucker 72%",
        "unit": "kg",
        "is_active": True,
        "description": "Zertifizierter Bio-Rübenzuckersirup"
    }, headers=admin_headers)
    assert new_ft_resp.status_code == 201
    new_ft = new_ft_resp.json()
    assert new_ft["name"] == "Bio-Invertzucker 72%"
    assert new_ft["unit"] == "kg"
    assert new_ft["is_active"] is True

    # Normal user cannot create feed type
    fail_ft = client.post("/api/admin/feed-types", json={
        "name": "Hacked Sugar",
        "unit": "kg"
    }, headers=normal_headers)
    assert fail_ft.status_code == 403

    # Update feed type as Admin
    up_ft_resp = client.put(f"/api/admin/feed-types/{new_ft['id']}", json={
        "name": "Bio-Invertzucker 72,7%",
        "unit": "l",
        "is_active": True,
        "description": "Angepasste Dichte"
    }, headers=admin_headers)
    assert up_ft_resp.status_code == 200
    assert up_ft_resp.json()["name"] == "Bio-Invertzucker 72,7%"
    assert up_ft_resp.json()["unit"] == "l"

    # Public active feed types list
    active_resp = client.get("/api/feedings/feed-types", headers=normal_headers)
    assert active_resp.status_code == 200
    assert any(ft["name"] == "Bio-Invertzucker 72,7%" for ft in active_resp.json())

    # 4. Setup Apiary, Location, FrameType, Hives
    apiary_resp = client.post("/api/apiaries", json={"name": "Fütterungs-Imkerei"}, headers=admin_headers)
    assert apiary_resp.status_code == 201
    apiary_id = apiary_resp.json()["id"]

    loc_resp = client.post(f"/api/locations?apiary_id={apiary_id}", json={"name": "Waldrand", "address": "Waldweg 1"}, headers=admin_headers)
    assert loc_resp.status_code == 201
    loc_id = loc_resp.json()["id"]

    ft_frame_resp = client.post("/api/admin/frame-types", json={"name": "Zander Feeding"}, headers=admin_headers)
    assert ft_frame_resp.status_code == 201
    frame_type_id = ft_frame_resp.json()["id"]

    hive1_resp = client.post(f"/api/hives?apiary_id={apiary_id}", json={
        "name": "Volk 1",
        "location_id": loc_id,
        "frame_type_id": frame_type_id
    }, headers=admin_headers)
    assert hive1_resp.status_code == 201
    hive1_id = hive1_resp.json()["id"]

    hive2_resp = client.post(f"/api/hives?apiary_id={apiary_id}", json={
        "name": "Volk 2",
        "location_id": loc_id,
        "frame_type_id": frame_type_id
    }, headers=admin_headers)
    assert hive2_resp.status_code == 201
    hive2_id = hive2_resp.json()["id"]

    # 5. Create Single Feeding
    feed1_resp = client.post("/api/feedings", json={
        "hive_id": hive1_id,
        "feed_type_id": new_ft["id"],
        "date": date.today().isoformat(),
        "amount": 2.5,
        "fed_by": "Imker Franz",
        "notes": "Erste Einfütterung"
    }, headers=admin_headers)
    assert feed1_resp.status_code == 201
    feed1 = feed1_resp.json()
    assert feed1["amount"] == 2.5
    assert feed1["hive"]["name"] == "Volk 1"
    assert feed1["feed_type"]["name"] == "Bio-Invertzucker 72,7%"
    assert feed1["fed_by"] == "Imker Franz"

    # Feed type deletion should be blocked while in use
    del_ft_fail = client.delete(f"/api/admin/feed-types/{new_ft['id']}", headers=admin_headers)
    assert del_ft_fail.status_code == 400

    # 6. Create Batch Feeding (multiple hives)
    batch_resp = client.post("/api/feedings/batch", json={
        "hive_ids": [hive1_id, hive2_id],
        "feed_type_id": new_ft["id"],
        "date": date.today().isoformat(),
        "amount": 5.0,
        "fed_by": "Imker Franz",
        "notes": "Zweite Fütterung im Block"
    }, headers=admin_headers)
    assert batch_resp.status_code == 201
    batch_list = batch_resp.json()
    assert len(batch_list) == 2

    # 7. List Feedings with filters
    list_all = client.get(f"/api/feedings?apiary_id={apiary_id}", headers=admin_headers)
    assert list_all.status_code == 200
    assert len(list_all.json()) == 3

    list_h2 = client.get(f"/api/feedings?apiary_id={apiary_id}&hive_id={hive2_id}", headers=admin_headers)
    assert list_h2.status_code == 200
    assert len(list_h2.json()) == 1

    # 8. Stats Summary
    stats_resp = client.get(f"/api/feedings/stats?apiary_id={apiary_id}", headers=admin_headers)
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert stats_data["total_count"] == 3
    # Hive1 got 2.5 + 5.0 = 7.5; Hive2 got 5.0 => total = 12.5
    assert stats_data["totals_by_unit"]["l"] == 12.5

    # 9. CSV Export
    csv_resp = client.get(f"/api/feedings/export/csv?apiary_id={apiary_id}", headers=admin_headers)
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    csv_text = csv_resp.content.decode("utf-8-sig")
    assert "Volk 1" in csv_text
    assert "Bio-Invertzucker" in csv_text

    # 10. Update Feeding
    up_feed_resp = client.put(f"/api/feedings/{feed1['id']}", json={
        "amount": 3.0,
        "notes": "Menge korrigiert"
    }, headers=admin_headers)
    assert up_feed_resp.status_code == 200
    assert up_feed_resp.json()["amount"] == 3.0
    assert up_feed_resp.json()["notes"] == "Menge korrigiert"

    # 11. Delete Feeding
    del_feed_resp = client.delete(f"/api/feedings/{feed1['id']}", headers=admin_headers)
    assert del_feed_resp.status_code == 204

    # Verification after delete
    list_after = client.get(f"/api/feedings?apiary_id={apiary_id}", headers=admin_headers)
    assert len(list_after.json()) == 2

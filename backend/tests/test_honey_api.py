from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.honey_batch import HoneyBatch, HoneyBottling

def test_honey_batch_lifecycle_and_validation(client: TestClient, db: Session):
    # 1. Register and login
    reg_response = client.post("/api/auth/register", json={
        "username": "honeytester",
        "email": "honeytester@example.com",
        "password": "strongpassword123",
        "first_name": "Honey",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "honeytester",
        "password": "strongpassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create an apiary for testing
    apiary_resp = client.post("/api/apiaries", json={
        "name": "Honey Apiary",
        "address": "Honey Lane 1"
    }, headers=headers)
    assert apiary_resp.status_code == 201
    apiary_id = apiary_resp.json()["id"]

    # 3. Try to create batch without batch_number when is_exact_date is False
    bad_batch_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "honey_type": "Sommertracht",
        "harvest_date": "2026-05-21",
        "quantity_kg": 50.0,
        "best_before_date": "2028-05-21",
        "is_exact_date": False
    }, headers=headers)
    assert bad_batch_resp.status_code == 422

    # 4. Create batch without batch_number when is_exact_date is True (MHD exception)
    mhd_ex_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "honey_type": "Sommertracht",
        "harvest_date": "2026-05-21",
        "quantity_kg": 25.5,
        "best_before_date": "2028-05-21",
        "is_exact_date": True
    }, headers=headers)
    assert mhd_ex_resp.status_code == 201
    mhd_batch = mhd_ex_resp.json()
    assert mhd_batch["batch_number"] is None
    assert mhd_batch["is_exact_date"] is True
    assert mhd_batch["bottlings"] == []
    assert mhd_batch["total_bottled_kg"] == 0.0

    # 5. Create valid batch with batch_number when is_exact_date is False
    good_batch_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "batch_number": "L123-2026",
        "honey_type": "Rapshonig",
        "harvest_date": "2026-05-20",
        "quantity_kg": 150.0,
        "water_content_percent": 16.5,
        "heating_temperature_celsius": 32.0,
        "best_before_date": "2028-05-20",
        "is_exact_date": False,
        "reserve_sample_taken": True,
        "reserve_sample_date": "2026-05-20",
        "reserve_sample_id": "RS-L123",
        "notes": "Premium quality honey"
    }, headers=headers)
    assert good_batch_resp.status_code == 201
    good_batch = good_batch_resp.json()
    batch_id = good_batch["id"]
    assert good_batch["batch_number"] == "L123-2026"
    assert good_batch["quantity_kg"] == 150.0
    assert good_batch["water_content_percent"] == 16.5
    assert len(good_batch["bottlings"]) == 0

    # 6. Add first bottling (Abfüllung 1: 100 x 500g DIB Gläser = 50 kg)
    bottling1_resp = client.post(f"/api/honey-batches/{batch_id}/bottlings", json={
        "bottling_date": "2026-05-25",
        "jar_size_g": 500,
        "quantity_jars": 100,
        "quantity_kg": 50.0,
        "notes": "Erste Abfüllung in DIB Gläser",
        "dib_ranges": [
            {"dib_label_start": "000100", "dib_label_end": "000199"}
        ]
    }, headers=headers)
    assert bottling1_resp.status_code == 201
    b1_data = bottling1_resp.json()
    b1_id = b1_data["id"]
    assert b1_data["jar_size_g"] == 500
    assert b1_data["quantity_jars"] == 100
    assert b1_data["quantity_kg"] == 50.0
    assert b1_data["dib_label_start"] == "000100"
    assert b1_data["dib_label_end"] == "000199"

    # 7. Add second bottling (Abfüllung 2: 80 x 250g Gläser = 20 kg)
    bottling2_resp = client.post(f"/api/honey-batches/{batch_id}/bottlings", json={
        "bottling_date": "2026-06-01",
        "jar_size_g": 250,
        "quantity_jars": 80,
        "quantity_kg": 20.0,
        "notes": "Zweite Abfüllung kleine Gläser",
        "dib_label_start": "000500",
        "dib_label_end": "000579"
    }, headers=headers)
    assert bottling2_resp.status_code == 201
    b2_data = bottling2_resp.json()
    b2_id = b2_data["id"]

    # 8. Get batch and verify aggregate totals and bottlings list
    get_batch_resp = client.get(f"/api/honey-batches/{batch_id}", headers=headers)
    assert get_batch_resp.status_code == 200
    batch_detail = get_batch_resp.json()
    assert len(batch_detail["bottlings"]) == 2
    assert batch_detail["total_bottled_kg"] == 70.0 # 50 + 20
    assert batch_detail["total_bottled_jars"] == 180 # 100 + 80

    # 9. List bottlings endpoint
    list_bottlings_resp = client.get(f"/api/honey-batches/{batch_id}/bottlings", headers=headers)
    assert list_bottlings_resp.status_code == 200
    assert len(list_bottlings_resp.json()) == 2

    # 10. Update bottling 2 (e.g. adjust jar count to 100 -> 25 kg)
    update_b2_resp = client.put(f"/api/honey-batches/{batch_id}/bottlings/{b2_id}", json={
        "quantity_jars": 100,
        "quantity_kg": 25.0,
        "notes": "Korrigiert auf 100 Gläser"
    }, headers=headers)
    assert update_b2_resp.status_code == 200
    assert update_b2_resp.json()["quantity_jars"] == 100
    assert update_b2_resp.json()["quantity_kg"] == 25.0

    # Verify updated aggregates on batch
    get_batch_resp2 = client.get(f"/api/honey-batches/{batch_id}", headers=headers)
    assert get_batch_resp2.json()["total_bottled_kg"] == 75.0
    assert get_batch_resp2.json()["total_bottled_jars"] == 200

    # 11. Delete bottling 1
    del_b1_resp = client.delete(f"/api/honey-batches/{batch_id}/bottlings/{b1_id}", headers=headers)
    assert del_b1_resp.status_code == 204

    # Verify only bottling 2 remains
    get_batch_resp3 = client.get(f"/api/honey-batches/{batch_id}", headers=headers)
    assert len(get_batch_resp3.json()["bottlings"]) == 1
    assert get_batch_resp3.json()["total_bottled_kg"] == 25.0

    # 12. Export CSV and check headers and contents
    export_resp = client.get(f"/api/honey-batches/export/csv?apiary_id={apiary_id}", headers=headers)
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"].startswith("text/csv")
    csv_text = export_resp.text
    assert "Sommertracht" in csv_text
    assert "Rapshonig" in csv_text
    assert "L123-2026" in csv_text
    assert "Abfülldatum" in csv_text

    # 13. Number range suggestion tests
    suggest_resp = client.get("/api/honey-batches/suggest-number?key=batch_number", headers=headers)
    assert suggest_resp.status_code == 200
    assert suggest_resp.json()["suggested_value"] == "LOT-0001"

    suggest_sample_resp = client.get("/api/honey-batches/suggest-number?key=reserve_sample_id", headers=headers)
    assert suggest_sample_resp.status_code == 200
    assert suggest_sample_resp.json()["suggested_value"] == "PRB-0001"

    # 14. Create a batch using suggested numbers
    suggested_batch_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "batch_number": "LOT-0001",
        "honey_type": "Waldhonig",
        "harvest_date": "2026-05-22",
        "quantity_kg": 50.0,
        "best_before_date": "2028-05-22",
        "is_exact_date": False,
        "reserve_sample_taken": True,
        "reserve_sample_date": "2026-05-22",
        "reserve_sample_id": "PRB-0001"
    }, headers=headers)
    assert suggested_batch_resp.status_code == 201

    # Suggestion should now be incremented to LOT-0002 and PRB-0002
    suggest_next_resp = client.get("/api/honey-batches/suggest-number?key=batch_number", headers=headers)
    assert suggest_next_resp.json()["suggested_value"] == "LOT-0002"

    suggest_next_sample = client.get("/api/honey-batches/suggest-number?key=reserve_sample_id", headers=headers)
    assert suggest_next_sample.json()["suggested_value"] == "PRB-0002"

    # 15. Try duplicate batch_number -> should fail
    duplicate_batch_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "batch_number": "LOT-0001",
        "honey_type": "Waldhonig",
        "harvest_date": "2026-05-23",
        "quantity_kg": 30.0,
        "best_before_date": "2028-05-23",
        "is_exact_date": False
    }, headers=headers)
    assert duplicate_batch_resp.status_code == 400
    assert "Los-/Chargennummer wird bereits verwendet" in duplicate_batch_resp.json()["detail"]

    # 16. Delete batch cascades to remaining bottlings
    del_batch_resp = client.delete(f"/api/honey-batches/{batch_id}", headers=headers)
    assert del_batch_resp.status_code == 204

    # Verify db deletion
    assert db.query(HoneyBatch).filter(HoneyBatch.id == batch_id).first() is None
    assert db.query(HoneyBottling).filter(HoneyBottling.id == b2_id).first() is None

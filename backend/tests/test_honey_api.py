from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.honey_batch import HoneyBatch

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
        "quantity_kg": 25.5,
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

    # 5. Create valid batch with batch_number when is_exact_date is False
    good_batch_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "batch_number": "L123-2026",
        "honey_type": "Rapshonig",
        "harvest_date": "2026-05-20",
        "bottling_date": "2026-05-21",
        "quantity_kg": 150.0,
        "water_content_percent": 16.5,
        "heating_temperature_celsius": 32.0,
        "best_before_date": "2028-05-20",
        "is_exact_date": False,
        "dib_label_start": "000100",
        "dib_label_end": "000399",
        "reserve_sample_taken": True,
        "reserve_sample_date": "2026-05-20",
        "reserve_sample_id": "RS-L123",
        "notes": "Premium quality honey"
    }, headers=headers)
    assert good_batch_resp.status_code == 201
    good_batch = good_batch_resp.json()
    assert good_batch["batch_number"] == "L123-2026"
    assert good_batch["quantity_kg"] == 150.0
    assert good_batch["water_content_percent"] == 16.5

    # 6. List batches for the apiary
    list_resp = client.get(f"/api/honey-batches?apiary_id={apiary_id}", headers=headers)
    assert list_resp.status_code == 200
    batches = list_resp.json()
    assert len(batches) == 2
    assert batches[0]["honey_type"] == "Sommertracht" # Descending harvest_date

    # 7. Update batch
    update_resp = client.put(f"/api/honey-batches/{good_batch['id']}", json={
        "quantity_kg": 145.0,
        "notes": "Updated notes"
    }, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["quantity_kg"] == 145.0
    assert update_resp.json()["notes"] == "Updated notes"

    # 8. Export CSV
    export_resp = client.get(f"/api/honey-batches/export/csv?apiary_id={apiary_id}", headers=headers)
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"].startswith("text/csv")
    csv_text = export_resp.text
    assert "Sommertracht" in csv_text
    assert "Rapshonig" in csv_text
    assert "L123-2026" in csv_text

    # 9. AI Draft Honey Batch
    ai_draft_resp = client.post("/api/ai/draft-honey", json={
        "text": "100kg Lindenhonig geerntet am 2026-05-15 mit 17% Wasser. Startnummer 1234 und Endnummer 1434"
    }, headers=headers)
    assert ai_draft_resp.status_code == 200
    draft = ai_draft_resp.json()["draft"]
    # Check fallback / parser mapping
    assert draft["honey_type"] in ["Lindenhonig", "Blütenhonig"]
    assert draft["quantity_kg"] > 0

    # 10. Number range suggestion tests
    suggest_resp = client.get("/api/honey-batches/suggest-number?key=batch_number", headers=headers)
    assert suggest_resp.status_code == 200
    assert suggest_resp.json()["suggested_value"] == "LOT-0001"

    suggest_sample_resp = client.get("/api/honey-batches/suggest-number?key=reserve_sample_id", headers=headers)
    assert suggest_sample_resp.status_code == 200
    assert suggest_sample_resp.json()["suggested_value"] == "PRB-0001"

    # 11. Create a batch using the suggested batch number (LOT-0001) and sample ID (PRB-0001)
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

    # 12. Try to create duplicate batch_number (LOT-0001) -> should fail
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

    # 13. Try to create duplicate reserve_sample_id (PRB-0001) -> should fail
    duplicate_sample_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "batch_number": "LOT-0002",
        "honey_type": "Waldhonig",
        "harvest_date": "2026-05-23",
        "quantity_kg": 30.0,
        "best_before_date": "2028-05-23",
        "is_exact_date": False,
        "reserve_sample_taken": True,
        "reserve_sample_date": "2026-05-23",
        "reserve_sample_id": "PRB-0001"
    }, headers=headers)
    assert duplicate_sample_resp.status_code == 400
    assert "Rückstellproben-ID wird bereits verwendet" in duplicate_sample_resp.json()["detail"]

    # 14. Create batch with multiple DIB ranges and test retrieval + update
    multi_range_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "batch_number": "LOT-MULTI",
        "honey_type": "Lindenhonig",
        "harvest_date": "2026-06-01",
        "quantity_kg": 80.0,
        "best_before_date": "2028-06-01",
        "is_exact_date": False,
        "dib_ranges": [
            {"dib_label_start": "200100", "dib_label_end": "200199"},
            {"dib_label_start": "200300", "dib_label_end": "200349"}
        ]
    }, headers=headers)
    assert multi_range_resp.status_code == 201
    created_multi = multi_range_resp.json()
    assert len(created_multi["dib_ranges"]) == 2
    assert created_multi["dib_ranges"][0]["dib_label_start"] == "200100"
    assert created_multi["dib_ranges"][1]["dib_label_end"] == "200349"
    # Legacy property compat assertion
    assert created_multi["dib_label_start"] == "200100"
    assert created_multi["dib_label_end"] == "200199"

    # Update with new ranges
    update_multi_resp = client.put(f"/api/honey-batches/{created_multi['id']}", json={
        "dib_ranges": [
            {"dib_label_start": "500000", "dib_label_end": "500050"}
        ]
    }, headers=headers)
    assert update_multi_resp.status_code == 200
    updated_multi = update_multi_resp.json()
    assert len(updated_multi["dib_ranges"]) == 1
    assert updated_multi["dib_ranges"][0]["dib_label_start"] == "500000"
    assert updated_multi["dib_label_start"] == "500000"



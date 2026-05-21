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

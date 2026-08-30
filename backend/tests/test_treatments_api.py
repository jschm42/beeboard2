from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import os

def test_treatments_and_methods_workflow(client: TestClient, db: Session):
    # 1. Register and login the first user (who becomes SYSTEM_ADMIN)
    reg_response = client.post("/api/auth/register", json={
        "username": "admintester",
        "email": "admintester@example.com",
        "password": "strongpassword123",
        "first_name": "Admin",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "admintester",
        "password": "strongpassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {token}"}

    # 2. Register and login a normal user
    reg_response2 = client.post("/api/auth/register", json={
        "username": "normaltester",
        "email": "normaltester@example.com",
        "password": "strongpassword123",
        "first_name": "Normal",
        "last_name": "Tester"
    })
    assert reg_response2.status_code == 201
    
    login_response2 = client.post("/api/auth/login", data={
        "username": "normaltester",
        "password": "strongpassword123"
    })
    assert login_response2.status_code == 200
    token2 = login_response2.json()["access_token"]
    normal_headers = {"Authorization": f"Bearer {token2}"}

    # 3. Test Admin treatment methods CRUD
    # List methods (seeded ones)
    methods_resp = client.get("/api/admin/treatment-methods", headers=admin_headers)
    assert methods_resp.status_code == 200
    initial_methods = methods_resp.json()
    assert len(initial_methods) >= 5  # seeded methods exist
    
    # Create method as Admin with manufacturer_info
    new_method_resp = client.post("/api/admin/treatment-methods", json={
        "name": "SuperAcid",
        "unit": "ml",
        "is_active": True,
        "manufacturer_info": "Hersteller: Imker-Bedarf AG\nRezeptur: 60%ige Lösung morgens anwenden."
    }, headers=admin_headers)
    assert new_method_resp.status_code == 201
    new_method = new_method_resp.json()
    assert new_method["name"] == "SuperAcid"
    assert new_method["manufacturer_info"] == "Hersteller: Imker-Bedarf AG\nRezeptur: 60%ige Lösung morgens anwenden."
    assert "attachments" in new_method

    # Upload attachment to Treatment Method (PDF / Text / Screenshot)
    pdf_content = b"%PDF-1.4 Mock PDF Content with recipe instructions"
    att_resp = client.post(
        f"/api/admin/treatment-methods/{new_method['id']}/attachments",
        files={"file": ("rezeptur_anleitung.pdf", pdf_content, "application/pdf")},
        headers=admin_headers
    )
    assert att_resp.status_code == 201
    att_data = att_resp.json()
    assert att_data["file_name"] == "rezeptur_anleitung.pdf"
    assert "rezeptur_anleitung.pdf" in att_data["file_path"]

    # Upload text attachment
    txt_content = b"Dosierung: 30ml pro Zarge bei Aussentemperatur 15-25 Grad"
    att_txt_resp = client.post(
        f"/api/admin/treatment-methods/{new_method['id']}/attachments",
        files={"file": ("dosierhinweis.txt", txt_content, "text/plain")},
        headers=admin_headers
    )
    assert att_txt_resp.status_code == 201
    att_txt_data = att_txt_resp.json()
    assert att_txt_data["file_name"] == "dosierhinweis.txt"

    # Delete one attachment
    del_att_resp = client.delete(f"/api/admin/treatment-methods/attachments/{att_txt_data['id']}", headers=admin_headers)
    assert del_att_resp.status_code == 204

    # Create method as normal user should fail
    fail_method_resp = client.post("/api/admin/treatment-methods", json={
        "name": "NormalAcid",
        "unit": "ml",
        "is_active": True
    }, headers=normal_headers)
    assert fail_method_resp.status_code == 403

    # Update method as Admin
    up_method_resp = client.put(f"/api/admin/treatment-methods/{new_method['id']}", json={
        "name": "SuperAcid Updated",
        "unit": "ml",
        "is_active": True,
        "manufacturer_info": "Hersteller: Updated AG"
    }, headers=admin_headers)
    assert up_method_resp.status_code == 200
    assert up_method_resp.json()["name"] == "SuperAcid Updated"
    assert up_method_resp.json()["manufacturer_info"] == "Hersteller: Updated AG"
    assert len(up_method_resp.json()["attachments"]) == 1

    # Test Admin treatment application types CRUD
    # List application types (seeded ones)
    apps_resp = client.get("/api/admin/treatment-application-types", headers=admin_headers)
    assert apps_resp.status_code == 200
    initial_apps = apps_resp.json()
    assert len(initial_apps) >= 3  # seeded types exist

    # Create application type as Admin
    new_app_resp = client.post("/api/admin/treatment-application-types", json={
        "name": "SuperSpraying",
        "is_active": True
    }, headers=admin_headers)
    assert new_app_resp.status_code == 201
    new_app = new_app_resp.json()
    assert new_app["name"] == "SuperSpraying"

    # Create application type as normal user should fail
    fail_app_resp = client.post("/api/admin/treatment-application-types", json={
        "name": "NormalSpraying",
        "is_active": True
    }, headers=normal_headers)
    assert fail_app_resp.status_code == 403

    # Update application type as Admin
    up_app_resp = client.put(f"/api/admin/treatment-application-types/{new_app['id']}", json={
        "name": "SuperSpraying Updated",
        "is_active": True
    }, headers=admin_headers)
    assert up_app_resp.status_code == 200
    assert up_app_resp.json()["name"] == "SuperSpraying Updated"

    # 4. Set up Apiary, Location, and Hive for regular treatment testing
    # Create Apiary as normal user
    apiary_resp = client.post("/api/apiaries", json={
        "name": "Normal Apiary"
    }, headers=normal_headers)
    assert apiary_resp.status_code == 201
    apiary_id = apiary_resp.json()["id"]

    # Create Location
    loc_resp = client.post("/api/locations", json={
        "name": "Normal Stand",
        "address": "Teststreet 1"
    }, params={"apiary_id": apiary_id}, headers=normal_headers)
    assert loc_resp.status_code == 201
    loc_id = loc_resp.json()["id"]

    # Get default frame type
    ft_resp = client.get("/api/hives/frame-types", headers=normal_headers)
    assert ft_resp.status_code == 200
    frame_type_id = ft_resp.json()[0]["id"]

    # Create Hive
    hive_resp = client.post("/api/hives", json={
        "name": "Volk A",
        "location_id": loc_id,
        "frame_type_id": frame_type_id,
        "is_active": True
    }, params={"apiary_id": apiary_id}, headers=normal_headers)
    assert hive_resp.status_code == 201
    hive_id = hive_resp.json()["id"]

    # 5. User Treatments CRUD
    # List active methods
    active_methods_resp = client.get("/api/treatments/methods", headers=normal_headers)
    assert active_methods_resp.status_code == 200
    active_methods = active_methods_resp.json()
    assert any(m["name"] == "SuperAcid Updated" for m in active_methods)

    # List active application types
    active_apps_resp = client.get("/api/treatments/application-types", headers=normal_headers)
    assert active_apps_resp.status_code == 200
    active_apps = active_apps_resp.json()
    assert any(a["name"] == "SuperSpraying Updated" for a in active_apps)

    # List treatment users (operators from admin)
    users_resp = client.get("/api/treatments/users", headers=normal_headers)
    assert users_resp.status_code == 200
    treatment_users = users_resp.json()
    assert len(treatment_users) >= 1
    assert any("full_name" in u for u in treatment_users)

    # Post treatment with period and operator (treated_by)
    treatment_resp = client.post("/api/treatments", json={
        "hive_id": hive_id,
        "treatment_method_id": new_method["id"],
        "application_type_id": new_app["id"],
        "date": "2026-07-14",
        "end_date": "2026-07-24",
        "amount": 45.5,
        "treated_by": "Dr. Imker",
        "notes": "Test treatment notes"
    }, headers=normal_headers)
    assert treatment_resp.status_code == 201
    treatment = treatment_resp.json()
    assert treatment["amount"] == 45.5
    assert treatment["notes"] == "Test treatment notes"
    assert treatment["end_date"] == "2026-07-24"
    assert treatment["treated_by"] == "Dr. Imker"
    assert treatment["hive"]["name"] == "Volk A"
    assert treatment["hive"]["location"]["name"] == "Normal Stand"
    assert treatment["application_type"]["name"] == "SuperSpraying Updated"

    # List treatments with filters
    list_resp = client.get("/api/treatments", params={"apiary_id": apiary_id}, headers=normal_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Export treatments as CSV
    csv_resp = client.get("/api/treatments/export/csv", params={"apiary_id": apiary_id}, headers=normal_headers)
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "attachment" in csv_resp.headers["content-disposition"]
    csv_content = csv_resp.content.decode("utf-8-sig")
    assert "Behandlungsmethode" in csv_content
    assert "Applikationsmethode" in csv_content
    assert "SuperSpraying Updated" in csv_content
    assert "2026-07-24" in csv_content
    assert "Dr. Imker" in csv_content

    # Export treatments as PDF (Bestandsbuch)
    pdf_resp = client.get("/api/treatments/export/pdf", params={"apiary_id": apiary_id}, headers=normal_headers)
    assert pdf_resp.status_code == 200
    assert "application/pdf" in pdf_resp.headers["content-type"]
    assert pdf_resp.content.startswith(b"%PDF")
    assert len(pdf_resp.content) > 500

    # Filter with hive_id
    list_filter_resp = client.get("/api/treatments", params={
        "apiary_id": apiary_id,
        "hive_id": hive_id
    }, headers=normal_headers)
    assert list_filter_resp.status_code == 200
    assert len(list_filter_resp.json()) == 1

    # Filter with incorrect dates (should return empty list)
    list_date_resp = client.get("/api/treatments", params={
        "apiary_id": apiary_id,
        "start_date": "2026-07-15"
    }, headers=normal_headers)
    assert list_date_resp.status_code == 200
    assert len(list_date_resp.json()) == 0

    # Put treatment
    up_treatment_resp = client.put(f"/api/treatments/{treatment['id']}", json={
        "amount": 50.0,
        "end_date": "2026-07-25",
        "treated_by": "Imkerin Anna",
        "notes": "Updated notes"
    }, headers=normal_headers)
    assert up_treatment_resp.status_code == 200
    assert up_treatment_resp.json()["amount"] == 50.0
    assert up_treatment_resp.json()["end_date"] == "2026-07-25"
    assert up_treatment_resp.json()["treated_by"] == "Imkerin Anna"
    assert up_treatment_resp.json()["notes"] == "Updated notes"

    # Upload Image (using mock file)
    mock_file_content = b"fake image bytes"
    img_resp = client.post(
        f"/api/treatments/{treatment['id']}/images",
        files={"file": ("test.jpg", mock_file_content, "image/jpeg")},
        headers=normal_headers
    )
    # Pillow might fail to parse 'fake image bytes' as a real image and fall back to thumbnail_path=None, but the endpoint should still return 201
    assert img_resp.status_code == 201
    img_data = img_resp.json()
    assert "image_path" in img_data

    # Delete Image
    del_img_resp = client.delete(f"/api/treatments/images/{img_data['id']}", headers=normal_headers)
    assert del_img_resp.status_code == 204

    # Delete Treatment Method used by treatment should fail
    del_method_fail = client.delete(f"/api/admin/treatment-methods/{new_method['id']}", headers=admin_headers)
    assert del_method_fail.status_code == 400

    # Delete Treatment Application Type used by treatment should fail
    del_app_fail = client.delete(f"/api/admin/treatment-application-types/{new_app['id']}", headers=admin_headers)
    assert del_app_fail.status_code == 400

    # Delete Treatment (requires apiary admin membership or system admin)
    # The normal user is the creator and automatically apiary ADMIN, so they can delete it.
    del_treatment_resp = client.delete(f"/api/treatments/{treatment['id']}", headers=normal_headers)
    assert del_treatment_resp.status_code == 204

    # Now deleting the treatment method should succeed since it's no longer used
    del_method_succ = client.delete(f"/api/admin/treatment-methods/{new_method['id']}", headers=admin_headers)
    assert del_method_succ.status_code == 204

    # Now deleting the application type should succeed since it's no longer used
    del_app_succ = client.delete(f"/api/admin/treatment-application-types/{new_app['id']}", headers=admin_headers)
    assert del_app_succ.status_code == 204

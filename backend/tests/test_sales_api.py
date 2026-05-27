from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_sales_lifecycle_and_tax_export(client: TestClient, _db: Session):
    # 1. Register and login
    reg_response = client.post("/api/auth/register", json={
        "username": "salestester",
        "email": "salestester@example.com",
        "password": "strongpassword123",
        "first_name": "Sales",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "salestester",
        "password": "strongpassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create products
    prod1_resp = client.post("/api/sales/products", json={
        "name": "Frühtracht 500g Glas",
        "honey_type": "Frühtracht",
        "price": 6.50,
        "tax_rate": 7.0,
        "is_active": True
    }, headers=headers)
    assert prod1_resp.status_code == 201
    prod1 = prod1_resp.json()
    assert prod1["name"] == "Frühtracht 500g Glas"
    assert prod1["price"] == 6.50

    prod2_resp = client.post("/api/sales/products", json={
        "name": "Met 0.75l Flasche",
        "honey_type": "Waldhonig",  # Met honey type mapping
        "price": 12.00,
        "tax_rate": 19.0,
        "is_active": True
    }, headers=headers)
    assert prod2_resp.status_code == 201
    prod2 = prod2_resp.json()

    # Create a product with omitted/null honey_type
    prod_null_resp = client.post("/api/sales/products", json={
        "name": "Wachskerze",
        "price": 4.50,
        "tax_rate": 19.0,
        "is_active": True
    }, headers=headers)
    assert prod_null_resp.status_code == 201
    prod_null = prod_null_resp.json()
    assert prod_null["honey_type"] is None

    # 3. List products
    list_prod_resp = client.get("/api/sales/products", headers=headers)
    assert list_prod_resp.status_code == 200
    products = list_prod_resp.json()
    assert len(products) == 3

    # 4. Create an apiary and a honey batch for linking
    apiary_resp = client.post("/api/apiaries", json={
        "name": "Sales Apiary",
        "address": "Sales Street 10"
    }, headers=headers)
    assert apiary_resp.status_code == 201
    apiary_id = apiary_resp.json()["id"]

    batch_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "batch_number": "L-SALE-01",
        "honey_type": "Frühtracht",
        "harvest_date": "2026-05-20",
        "quantity_kg": 50.0,
        "best_before_date": "2028-05-20",
        "is_exact_date": False
    }, headers=headers)
    assert batch_resp.status_code == 201
    batch = batch_resp.json()
    batch_id = batch["id"]

    # 5. Create a honey sale with auto-calculated total_price
    sale1_resp = client.post("/api/sales", json={
        "product_id": prod1["id"],
        "batch_id": batch_id,
        "quantity": 3.0,
        "sales_channel": "direktverkauf",
        "notes": "Bar gezahlt"
    }, headers=headers)
    assert sale1_resp.status_code == 201
    sale1 = sale1_resp.json()
    assert sale1["total_price"] == 19.50  # 6.50 * 3.0
    assert sale1["sales_channel"] == "direktverkauf"
    assert sale1["product"]["name"] == "Frühtracht 500g Glas"
    assert sale1["batch"]["batch_number"] == "L-SALE-01"

    # 6. Create another honey sale with custom/overridden price
    sale2_resp = client.post("/api/sales", json={
        "product_id": prod2["id"],
        "quantity": 2,
        "total_price": 20.00,  # Discounted from 24.00
        "sales_channel": "verkaufsstand",
        "notes": "Mengenrabatt"
    }, headers=headers)
    assert sale2_resp.status_code == 201
    sale2 = sale2_resp.json()
    assert sale2["total_price"] == 20.00
    assert sale2["batch"] is None

    # 7. List sales
    list_sales_resp = client.get("/api/sales", headers=headers)
    assert list_sales_resp.status_code == 200
    sales = list_sales_resp.json()
    assert len(sales) == 2

    # 8. Try to delete a product that is referenced by a sale (should fail)
    del_prod_resp = client.delete(f"/api/sales/products/{prod1['id']}", headers=headers)
    assert del_prod_resp.status_code == 400
    assert "Produkt kann nicht gelöscht werden" in del_prod_resp.json()["detail"]

    # 9. Update a sale
    upd_sale_resp = client.put(f"/api/sales/{sale1['id']}", json={
        "quantity": 4.0,
        "total_price": 25.00
    }, headers=headers)
    assert upd_sale_resp.status_code == 200
    assert upd_sale_resp.json()["quantity"] == 4.0
    assert upd_sale_resp.json()["total_price"] == 25.00

    # 10. Export tax CSV
    csv_resp = client.get("/api/sales/export/csv", headers=headers)
    assert csv_resp.status_code == 200
    assert csv_resp.headers["content-type"].startswith("text/csv")
    csv_text = csv_resp.text
    assert "Datum" in csv_text
    assert "Produkt" in csv_text
    assert "Steuersatz" in csv_text
    assert "Frühtracht 500g Glas" in csv_text
    assert "Met 0.75l Flasche" in csv_text
    assert "L-SALE-01" in csv_text
    assert "Bar gezahlt" in csv_text


def test_sales_tax_calculation_disabled(client: TestClient, db: Session):
    from app.services.ai_assistant import get_llm_config
    
    # Disable tax calculation in DB
    config = get_llm_config(db)
    config.calculate_taxes = False
    db.commit()

    # 1. Register and login
    reg_response = client.post("/api/auth/register", json={
        "username": "taxkeytester",
        "email": "taxkeytester@example.com",
        "password": "strongpassword123",
        "first_name": "Tax",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "taxkeytester",
        "password": "strongpassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get tax-settings
    settings_resp = client.get("/api/sales/tax-settings", headers=headers)
    assert settings_resp.status_code == 200
    assert settings_resp.json()["calculate_taxes"] is False

    # 3. Create product (tax_rate is ignored in CSV when tax calculation is disabled)
    prod_resp = client.post("/api/sales/products", json={
        "name": "Kleinunternehmer Honig",
        "honey_type": "Blütenhonig",
        "price": 5.00,
        "tax_rate": 7.0,
        "is_active": True
    }, headers=headers)
    assert prod_resp.status_code == 201
    prod = prod_resp.json()

    # 4. Create sale
    sale_resp = client.post("/api/sales", json={
        "product_id": prod["id"],
        "quantity": 1,
        "sales_channel": "direktverkauf",
        "notes": "Keine Steuer"
    }, headers=headers)
    assert sale_resp.status_code == 201

    # 5. Export tax CSV
    csv_resp = client.get("/api/sales/export/csv", headers=headers)
    assert csv_resp.status_code == 200
    csv_lines = csv_resp.text.strip().split("\n")
    
    # Read CSV rows, check Steuersatz
    headers_row = csv_lines[0].strip().split(";")
    steuersatz_idx = headers_row.index("Steuersatz")
    
    # Check the data row
    data_row = csv_lines[1].strip().split(";")
    assert data_row[steuersatz_idx] == "0,0"



def test_requires_batch_selection_enforcement(client, _db):
    """requires_batch_selection flag is stored and enforced at sale creation."""
    client.post('/api/auth/register', json={
        'username': 'batchtester', 'email': 'batchtester@example.com',
        'password': 'strongpassword123', 'first_name': 'Batch', 'last_name': 'Tester'
    })
    login_resp = client.post('/api/auth/login', data={
        'username': 'batchtester', 'password': 'strongpassword123'
    })
    headers = {'Authorization': 'Bearer ' + login_resp.json()['access_token']}

    # Product with required batch
    prod = client.post('/api/sales/products', json={
        'name': 'Traced Honey 250g', 'honey_type': 'Frühlingshonig',
        'price': 5.00, 'tax_rate': 7.0, 'is_active': True,
        'requires_batch_selection': True
    }, headers=headers).json()
    assert prod['requires_batch_selection'] is True

    # Sale without batch must be rejected
    resp = client.post('/api/sales', json={
        'product_id': prod['id'], 'quantity': 1, 'sales_channel': 'direktverkauf'
    }, headers=headers)
    assert resp.status_code == 422
    assert 'Losnummer' in resp.json()['detail']

    # Create apiary + batch
    apiary_id = client.post('/api/apiaries', json={
        'name': 'Batch Enforcement Apiary', 'address': 'Test 1'
    }, headers=headers).json()['id']
    batch_id = client.post(
        '/api/honey-batches?apiary_id=' + apiary_id, json={
            'batch_number': 'L-BATCH-ENF-01', 'honey_type': 'Fruehling',
            'harvest_date': '2026-05-01', 'quantity_kg': 20.0,
            'best_before_date': '2028-05-01', 'is_exact_date': False
        }, headers=headers
    ).json()['id']

    # Sale WITH batch must succeed
    resp2 = client.post('/api/sales', json={
        'product_id': prod['id'], 'quantity': 2,
        'sales_channel': 'direktverkauf', 'batch_id': batch_id
    }, headers=headers)
    assert resp2.status_code == 201
    assert resp2.json()['batch']['batch_number'] == 'L-BATCH-ENF-01'

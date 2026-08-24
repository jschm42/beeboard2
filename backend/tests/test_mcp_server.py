import pytest
from datetime import date, datetime
from unittest.mock import patch
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.apiary import Apiary, ApiaryMembership
from app.models.location import Location
from app.models.hive import Hive
from app.models.sales import ProductConfig, HoneySale
from app.models.task import Task
from app.models.treatment import Treatment, TreatmentMethod, TreatmentApplicationType
from app.models.logbook import LogEntry, InspectionDetail, InspectionBox

from app.mcp_server import (
    list_sales_products,
    create_honey_sale,
    list_honey_sales,
    get_hive_inspection_stats,
    list_tasks,
    create_task,
    list_treatments,
    create_treatment,
    list_treatment_methods,
    list_treatment_application_types
)

@pytest.fixture(autouse=True)
def mock_session_local(db: Session):
    # Patch close to prevent closing the transaction-managed db session
    original_close = db.close
    db.close = lambda: None
    with patch("app.mcp_server.SessionLocal", return_value=db):
        yield
    db.close = original_close

@pytest.fixture
def test_user(db: Session):
    user = User(
        username="mcp_tester",
        email="mcp_tester@example.com",
        hashed_password="fakehashedpwd",
        is_active=True,
        role="USER"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_apiary(db: Session, test_user: User):
    apiary = Apiary(
        name="MCP Apiary",
        notes="An apiary for testing MCP tools"
    )
    db.add(apiary)
    db.commit()
    db.refresh(apiary)
    
    membership = ApiaryMembership(
        apiary_id=apiary.id,
        user_id=test_user.id,
        role="ADMIN"
    )
    db.add(membership)
    db.commit()
    return apiary

@pytest.fixture
def test_location(db: Session, test_apiary: Apiary, test_user: User):
    location = Location(
        name="MCP Location",
        address="Location Street 1",
        apiary_id=test_apiary.id,
        created_by_id=test_user.id
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

@pytest.fixture
def test_hive(db: Session, test_apiary: Apiary, test_location: Location):
    # Get a frame type seeded by default
    from app.models.administration import FrameType
    zander = db.query(FrameType).filter(FrameType.name == "Zander").first()
    
    hive = Hive(
        name="MCP Hive 1",
        apiary_id=test_apiary.id,
        location_id=test_location.id,
        is_active=True,
        frame_type_id=zander.id
    )
    db.add(hive)
    db.commit()
    db.refresh(hive)
    return hive

def test_sales_mcp_tools(db: Session, test_user: User, test_apiary: Apiary):
    # 1. Test empty products list
    res_list_empty = list_sales_products()
    assert "Keine Produktkonfigurationen gefunden." in res_list_empty
    
    # 2. Create products
    p1 = ProductConfig(
        name="Meli-Honey 500g",
        price=7.50,
        tax_rate=7.0,
        is_active=True,
        manage_stock=True,
        stock=10.0,
        created_by_id=test_user.id
    )
    p2 = ProductConfig(
        name="Meli-Wax 1kg",
        price=15.00,
        tax_rate=19.0,
        is_active=False,
        manage_stock=False,
        created_by_id=test_user.id
    )
    db.add_all([p1, p2])
    db.commit()
    
    # Test listing active products only
    res_list_active = list_sales_products(is_active=True)
    assert "Meli-Honey 500g" in res_list_active
    assert "Meli-Wax 1kg" not in res_list_active
    
    # Test listing all products
    res_list_all = list_sales_products(is_active=False)
    assert "Meli-Honey 500g" in res_list_all
    assert "Meli-Wax 1kg" in res_list_all
    
    # 3. Create honey sale with default price
    res_sale = create_honey_sale(
        product_id=p1.id,
        quantity=2.0,
        sales_channel="verkaufsstand",
        buyer="John Doe",
        notes="Fast transaction"
    )
    assert "Verkauf erfolgreich erfasst!" in res_sale
    assert "Meli-Honey 500g" in res_sale
    assert "Menge: 2.0" in res_sale
    assert "Gesamtpreis: 15.0 EUR" in res_sale
    
    # Check that stock was reduced
    db.refresh(p1)
    assert p1.stock == 8.0
    
    # 4. List honey sales
    res_sales_list = list_honey_sales()
    assert "Meli-Honey 500g" in res_sales_list
    assert "Käufer: John Doe" in res_sales_list
    
    # List with date filtering
    res_sales_filtered = list_honey_sales(start_date_str="2020-01-01", end_date_str="2030-12-31")
    assert "Meli-Honey 500g" in res_sales_filtered

def test_inspection_stats_mcp_tool(db: Session, test_hive: Hive):
    # 1. Test no inspections
    res_empty = get_hive_inspection_stats(hive_id=test_hive.id)
    assert "Keine Inspektionseinträge" in res_empty
    
    # 2. Add an inspection with detail and boxes
    log_entry = LogEntry(
        hive_id=test_hive.id,
        apiary_id=test_hive.apiary_id,
        created_by_id=test_hive.apiary.memberships[0].user_id,
        date=date(2026, 7, 10),
        entry_type="INSPECTION",
        notes="All good"
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    detail = InspectionDetail(
        log_entry_id=log_entry.id
    )
    db.add(detail)
    db.commit()
    db.refresh(detail)
    
    box = InspectionBox(
        inspection_id=detail.id,
        box_index=0,
        brood_eighths=4,  # Zander: 4 * 400 = 1600 brood
        food_eighths=2,   # Zander: 2 * 125 = 250 food
        bee_eighths=6     # Zander: 6 * 125 = 750 bees
    )
    db.add(box)
    db.commit()
    
    # 3. Test retrieving statistics
    stats_res = get_hive_inspection_stats(hive_id=test_hive.id)
    assert f"Inspektionsstatistiken für Volk '{test_hive.name}'" in stats_res
    assert "Brutwaben: 1600.0" in stats_res
    assert "Futterwaben: 250.0" in stats_res
    assert "Bienen-Gassen: 750.0" in stats_res
    assert "All good" in stats_res

def test_tasks_mcp_tools(db: Session, test_apiary: Apiary, test_hive: Hive):
    # 1. List tasks (empty)
    res_list_empty = list_tasks(apiary_id=test_apiary.id)
    assert "Keine Aufgaben gefunden." in res_list_empty
    
    # 2. Create task
    res_create = create_task(
        apiary_id=test_apiary.id,
        title="Futterkontrolle",
        description="Winterfutter wiegen",
        due_date_str="2026-08-15",
        priority="HIGH",
        hive_id=test_hive.id
    )
    assert "Aufgabe erfolgreich angelegt!" in res_create
    assert "Futterkontrolle" in res_create
    assert "Priorität: HIGH" in res_create
    
    # 3. List tasks
    res_list = list_tasks(apiary_id=test_apiary.id, is_completed=False)
    assert "Futterkontrolle" in res_list
    assert "Fällig am: 2026-08-15" in res_list

def test_treatments_mcp_tools(db: Session, test_apiary: Apiary, test_hive: Hive):
    # 1. List methods & application types
    res_methods = list_treatment_methods()
    assert "Oxalsäure" in res_methods
    assert "Ameisensäure" in res_methods
    
    res_apps = list_treatment_application_types()
    assert "sprühen" in res_apps
    assert "beträufeln" in res_apps
    
    # Get oxalsaeure method id
    method = db.query(TreatmentMethod).filter(TreatmentMethod.name == "Oxalsäure").first()
    app_type = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.name == "beträufeln").first()
    
    # 2. Create treatment
    res_create = create_treatment(
        hive_id=test_hive.id,
        treatment_method_id=method.id,
        amount=50.0,
        date_str="2026-07-25",
        application_type_id=app_type.id,
        notes="Varroabehandlung Sommer"
    )
    assert "Behandlung erfolgreich erfasst!" in res_create
    assert "Oxalsäure" in res_create
    assert "Menge: 50.0 ml" in res_create
    
    # 3. List treatments
    res_list = list_treatments(apiary_id=test_apiary.id)
    assert "Oxalsäure" in res_list
    assert "Menge: 50.0 ml" in res_list
    assert "Varroabehandlung Sommer" in res_list

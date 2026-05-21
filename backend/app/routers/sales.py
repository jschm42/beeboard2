from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import csv
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.sales import ProductConfig, HoneySale
from app.models.honey_batch import HoneyBatch
from app.schemas.sales import (
    ProductConfigCreate, ProductConfigUpdate, ProductConfigOut,
    HoneySaleCreate, HoneySaleUpdate, HoneySaleOut
)
from app.routers.apiaries import check_access

router = APIRouter(prefix="/sales", tags=["sales"])

# --- Product Config Endpoints ---

@router.get("/products", response_model=List[ProductConfigOut])
def list_products(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all product configurations for the current user."""
    query = db.query(ProductConfig).filter(ProductConfig.created_by_id == current_user.id)
    if is_active is not None:
        query = query.filter(ProductConfig.is_active == is_active)
    return query.order_by(ProductConfig.name).all()

@router.post("/products", response_model=ProductConfigOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new product configuration."""
    new_product = ProductConfig(
        name=product_in.name,
        honey_type=product_in.honey_type,
        price=product_in.price,
        tax_rate=product_in.tax_rate,
        is_active=product_in.is_active,
        requires_batch_selection=product_in.requires_batch_selection,
        created_by_id=current_user.id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/products/{product_id}", response_model=ProductConfigOut)
def update_product(
    product_id: str,
    product_in: ProductConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates an existing product configuration."""
    product = db.query(ProductConfig).filter(
        ProductConfig.id == product_id,
        ProductConfig.created_by_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produktkonfiguration nicht gefunden")

    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a product configuration."""
    product = db.query(ProductConfig).filter(
        ProductConfig.id == product_id,
        ProductConfig.created_by_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produktkonfiguration nicht gefunden")

    # Check if there are sales referencing this product
    has_sales = db.query(HoneySale).filter(HoneySale.product_id == product_id).first()
    if has_sales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produkt kann nicht gelöscht werden, da es bereits in Verkäufen verwendet wird. Deaktivieren Sie es stattdessen."
        )

    db.delete(product)
    db.commit()
    return


# --- Honey Sales Endpoints ---

@router.get("", response_model=List[HoneySaleOut])
def list_sales(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all honey sales for the current user, optionally filtered by date."""
    query = db.query(HoneySale).filter(HoneySale.created_by_id == current_user.id)
    if start_date:
        query = query.filter(HoneySale.sale_date >= start_date)
    if end_date:
        query = query.filter(HoneySale.sale_date <= end_date)
    return query.order_by(HoneySale.sale_date.desc()).all()

@router.post("", response_model=HoneySaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale_in: HoneySaleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new honey sale transaction."""
    # Validate product exists and belongs to the user
    product = db.query(ProductConfig).filter(
        ProductConfig.id == sale_in.product_id,
        ProductConfig.created_by_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produktkonfiguration nicht gefunden")

    # Validate batch exists and user has access to its apiary
    if sale_in.batch_id:
        batch = db.query(HoneyBatch).filter(HoneyBatch.id == sale_in.batch_id).first()
        if not batch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Honig-Charge nicht gefunden")
        check_access(batch.apiary_id, current_user, db)

    # Enforce batch selection if required by product
    if product.requires_batch_selection and not sale_in.batch_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Für das Produkt '{product.name}' ist die Angabe einer Losnummer (Charge) zwingend erforderlich."
        )

    # Compute total price if not provided
    total_price = sale_in.total_price
    if total_price is None:
        total_price = product.price * sale_in.quantity

    new_sale = HoneySale(
        sale_date=sale_in.sale_date or datetime.now(),
        product_id=sale_in.product_id,
        batch_id=sale_in.batch_id,
        quantity=sale_in.quantity,
        total_price=total_price,
        sales_channel=sale_in.sales_channel,
        notes=sale_in.notes,
        buyer=sale_in.buyer,
        created_by_id=current_user.id
    )
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return new_sale

@router.put("/{sale_id}", response_model=HoneySaleOut)
def update_sale(
    sale_id: str,
    sale_in: HoneySaleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates an existing honey sale transaction."""
    sale = db.query(HoneySale).filter(
        HoneySale.id == sale_id,
        HoneySale.created_by_id == current_user.id
    ).first()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verkaufstransaktion nicht gefunden")

    # Validate product if updated
    if sale_in.product_id and sale_in.product_id != sale.product_id:
        product = db.query(ProductConfig).filter(
            ProductConfig.id == sale_in.product_id,
            ProductConfig.created_by_id == current_user.id
        ).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produktkonfiguration nicht gefunden")

    # Validate batch if updated
    if sale_in.batch_id and sale_in.batch_id != sale.batch_id:
        batch = db.query(HoneyBatch).filter(HoneyBatch.id == sale_in.batch_id).first()
        if not batch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Honig-Charge nicht gefunden")
        check_access(batch.apiary_id, current_user, db)

    # Re-validate batch requirement after potential product/batch changes
    effective_product_id = sale_in.product_id or sale.product_id
    effective_batch_id = sale_in.batch_id if 'batch_id' in sale_in.model_fields_set else sale.batch_id
    effective_product = db.query(ProductConfig).filter(ProductConfig.id == effective_product_id).first()
    if effective_product and effective_product.requires_batch_selection and not effective_batch_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Für das Produkt '{effective_product.name}' ist die Angabe einer Losnummer (Charge) zwingend erforderlich."
        )

    for field, value in sale_in.model_dump(exclude_unset=True).items():
        setattr(sale, field, value)

    db.commit()
    db.refresh(sale)
    return sale

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a honey sale transaction."""
    sale = db.query(HoneySale).filter(
        HoneySale.id == sale_id,
        HoneySale.created_by_id == current_user.id
    ).first()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verkaufstransaktion nicht gefunden")

    db.delete(sale)
    db.commit()
    return


@router.get("/tax-settings")
def get_tax_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves the system-wide tax settings (e.g. Kleinunternehmer-Regelung)."""
    from app.services.ai_assistant import get_llm_config
    config = get_llm_config(db)
    return {"kleinunternehmer_regelung": config.kleinunternehmer_regelung}


# --- Tax CSV Export ---

@router.get("/export/csv")
def export_sales_csv(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exports sales transactions for the current user to a CSV file for tax purposes."""
    query = db.query(HoneySale).filter(HoneySale.created_by_id == current_user.id)
    if start_date:
        query = query.filter(HoneySale.sale_date >= start_date)
    if end_date:
        query = query.filter(HoneySale.sale_date <= end_date)
    
    from app.services.ai_assistant import get_llm_config
    config = get_llm_config(db)
    is_kleinunternehmer = config.kleinunternehmer_regelung

    sales = query.order_by(HoneySale.sale_date.asc()).all()

    # Generate CSV in memory with utf-8-sig BOM for Excel compatibility
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')

    # Headers in German as requested
    writer.writerow([
        "Datum",
        "Produkt",
        "Menge",
        "Gesamtpreis",
        "Steuersatz",
        "Kanal",
        "Chargennummer",
        "Verkauft an",
        "Notizen"
    ])

    for s in sales:
        # Format values
        datum_str = s.sale_date.strftime("%d.%m.%Y %H:%M") if s.sale_date else ""
        product_name = s.product.name if s.product else "Gelöschtes Produkt"
        menge_str = str(s.quantity).replace('.', ',')
        price_str = str(round(s.total_price, 2)).replace('.', ',')
        if is_kleinunternehmer:
            tax_str = "0,0"
        else:
            tax_str = str(s.product.tax_rate).replace('.', ',') if s.product else "0,0"
        channel_str = s.sales_channel
        # Map channel keys to German readable text
        channel_map = {
            "direktverkauf": "Direktverkauf",
            "online": "Online",
            "email": "E-Mail",
            "verkaufsstand": "Verkaufsstand"
        }
        channel_str = channel_map.get(channel_str, channel_str)
        batch_num = s.batch.batch_number if s.batch else ""
        buyer_str = s.buyer or ""
        notizen_str = s.notes or ""

        writer.writerow([
            datum_str,
            product_name,
            menge_str,
            price_str,
            tax_str,
            channel_str,
            batch_num,
            buyer_str,
            notizen_str
        ])

    csv_data = output.getvalue()
    output.close()

    filename = f"honigverkaeufe_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        io.BytesIO(csv_data.encode("utf-8")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationOut
from app.routers.apiaries import check_access
from app.services.weather import geocode_address

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("", response_model=List[LocationOut])
def list_locations(
    apiary_id: str = Query(..., description="Scope search to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all locations for a specific authorized apiary."""
    check_access(apiary_id, current_user, db)
    return db.query(Location).options(joinedload(Location.hives)).filter(
        Location.apiary_id == apiary_id
    ).order_by(Location.name).all()

@router.post("", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(
    location_in: LocationCreate,
    apiary_id: str = Query(..., description="Scope creation to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new stand/location inside an authorized apiary."""
    check_access(apiary_id, current_user, db)
    
    new_location = Location(
        name=location_in.name,
        address=location_in.address,
        latitude=location_in.latitude,
        longitude=location_in.longitude,
        notes=location_in.notes,
        apiary_id=apiary_id,
        created_by_id=current_user.id
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location

@router.get("/geocode")
async def geocode(
    address: str = Query(..., description="The address/city to geocode"),
    current_user: User = Depends(get_current_user)
):
    """Geocodes an address to latitude and longitude."""
    res = await geocode_address(address)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keine Koordinaten für diese Adresse gefunden oder API-Schlüssel nicht konfiguriert."
        )
    return res

@router.get("/{location_id}", response_model=LocationOut)
def get_location(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves a single location by ID after validating authorization."""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Standort nicht gefunden")
    
    check_access(location.apiary_id, current_user, db)
    return location

@router.put("/{location_id}", response_model=LocationOut)
def update_location(
    location_id: str,
    location_in: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates location coordinates, address, and notes."""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Standort nicht gefunden")
    
    check_access(location.apiary_id, current_user, db)
    
    location.name = location_in.name
    location.address = location_in.address
    location.latitude = location_in.latitude
    location.longitude = location_in.longitude
    location.notes = location_in.notes
    
    db.commit()
    db.refresh(location)
    return location

@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes location from database. Protects against deletion if referenced by active hives (cascade or protect)."""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Standort nicht gefunden")
    
    check_access(location.apiary_id, current_user, db, require_admin=True)
    
    # Check if there are active hives at this location
    if len(location.hives) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Standort kann nicht gelöscht werden, da ihm noch Bienenvölker zugeordnet sind"
        )
        
    db.delete(location)
    db.commit()
    return

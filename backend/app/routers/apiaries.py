from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.apiary import Apiary, ApiaryMembership
from app.schemas.apiary import ApiaryCreate, ApiaryOut, ApiaryMembershipOut, ApiaryMembershipCreate

router = APIRouter(prefix="/apiaries", tags=["apiaries"])

def check_access(apiary_id: str, user: User, db: Session, require_admin: bool = False) -> ApiaryMembership:
    # SYSTEM_ADMIN is granted global bypass access
    if user.role == "SYSTEM_ADMIN":
        # Check if apiary actually exists
        apiary = db.query(Apiary).filter(Apiary.id == apiary_id).first()
        if not apiary:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imkerei nicht gefunden")
        # Return a mock membership for administrative bypass
        return ApiaryMembership(apiary_id=apiary_id, user_id=user.id, role="ADMIN")

    membership = db.query(ApiaryMembership).filter(
        ApiaryMembership.apiary_id == apiary_id,
        ApiaryMembership.user_id == user.id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sie haben keinen Zugriff auf diese Imkerei"
        )
    if require_admin and membership.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrationsrechte für diese Imkerei erforderlich"
        )
    return membership

@router.get("", response_model=List[ApiaryOut])
def list_apiaries(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all apiaries current user has access to."""
    if current_user.role == "SYSTEM_ADMIN":
        return db.query(Apiary).order_by(Apiary.name).all()
        
    return db.query(Apiary).join(ApiaryMembership).filter(
        ApiaryMembership.user_id == current_user.id
    ).order_by(Apiary.name).all()

@router.post("", response_model=ApiaryOut, status_code=status.HTTP_201_CREATED)
def create_apiary(apiary_in: ApiaryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Creates a new apiary and automatically adds current user as ADMIN."""
    new_apiary = Apiary(
        name=apiary_in.name,
        notes=apiary_in.notes
    )
    db.add(new_apiary)
    db.commit()
    db.refresh(new_apiary)

    # Add membership
    membership = ApiaryMembership(
        apiary_id=new_apiary.id,
        user_id=current_user.id,
        role="ADMIN"
    )
    db.add(membership)
    db.commit()

    return new_apiary

@router.get("/{apiary_id}", response_model=ApiaryOut)
def get_apiary(apiary_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieves apiary details if authorized."""
    check_access(apiary_id, current_user, db)
    apiary = db.query(Apiary).filter(Apiary.id == apiary_id).first()
    if not apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imkerei nicht gefunden")
    return apiary

@router.put("/{apiary_id}", response_model=ApiaryOut)
def update_apiary(apiary_id: str, apiary_in: ApiaryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Updates apiary if current user is an ADMIN of the apiary."""
    check_access(apiary_id, current_user, db, require_admin=True)
    apiary = db.query(Apiary).filter(Apiary.id == apiary_id).first()
    if not apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imkerei nicht gefunden")
    
    apiary.name = apiary_in.name
    apiary.notes = apiary_in.notes
    db.commit()
    db.refresh(apiary)
    return apiary

@router.delete("/{apiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_apiary(apiary_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deletes apiary if current user is an ADMIN of the apiary."""
    check_access(apiary_id, current_user, db, require_admin=True)
    apiary = db.query(Apiary).filter(Apiary.id == apiary_id).first()
    if not apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imkerei nicht gefunden")
    db.delete(apiary)
    db.commit()
    return

@router.get("/{apiary_id}/members", response_model=List[ApiaryMembershipOut])
def list_apiary_members(apiary_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all members of the apiary."""
    check_access(apiary_id, current_user, db)
    return db.query(ApiaryMembership).filter(ApiaryMembership.apiary_id == apiary_id).all()

@router.post("/{apiary_id}/members", response_model=ApiaryMembershipOut, status_code=status.HTTP_201_CREATED)
def add_apiary_member(apiary_id: str, member_in: ApiaryMembershipCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Adds or invites a user to the apiary. Only apiary ADMINs can invite."""
    check_access(apiary_id, current_user, db, require_admin=True)
    
    target_user = db.query(User).filter(
        (User.username == member_in.username_or_email) | (User.email == member_in.username_or_email)
    ).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benutzer mit diesem Namen oder E-Mail nicht gefunden"
        )

    # Check if membership already exists
    existing = db.query(ApiaryMembership).filter(
        ApiaryMembership.apiary_id == apiary_id,
        ApiaryMembership.user_id == target_user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benutzer ist bereits Mitglied dieser Imkerei"
        )

    new_membership = ApiaryMembership(
        apiary_id=apiary_id,
        user_id=target_user.id,
        role=member_in.role
    )
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)
    return new_membership

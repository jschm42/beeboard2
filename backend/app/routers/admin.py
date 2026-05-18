from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.administration import LLMConfig
from app.schemas.user import UserOut
from app.schemas.admin import LLMConfigOut, LLMConfigUpdate, UserAdminUpdate
from app.services.ai_assistant import get_llm_config

router = APIRouter(prefix="/admin", tags=["admin"])

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to check if the current user is a SYSTEM_ADMIN."""
    if current_user.role != "SYSTEM_ADMIN" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Zugriff verweigert. Nur Administratoren haben Zugriff auf diesen Bereich."
        )
    return current_user

@router.get("/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Lists all users in the system."""
    return db.query(User).order_by(User.username).all()

@router.put("/users/{user_id}", response_model=UserOut)
def update_user_admin(
    user_id: str,
    payload: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Updates a user's role or active status (admin only, blocks self-lockout)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benutzer nicht gefunden."
        )

    # Self lockout prevention
    if user.id == current_admin.id:
        if payload.role is not None and payload.role != "SYSTEM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Du kannst deine eigene Administrator-Rolle nicht entfernen."
            )
        if payload.is_active is not None and not payload.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Du kannst dein eigenes Benutzerkonto nicht deaktivieren."
            )

    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    return user

@router.get("/llm-config", response_model=LLMConfigOut)
def read_llm_config(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Retrieves the system-wide LLM prompts and configurations."""
    return get_llm_config(db)

@router.put("/llm-config", response_model=LLMConfigOut)
def update_llm_config(
    payload: LLMConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Updates the system-wide LLM prompts and weather API settings."""
    config = get_llm_config(db)

    if payload.chatbot_system_prompt is not None:
        config.chatbot_system_prompt = payload.chatbot_system_prompt
    if payload.draft_system_prompt is not None:
        config.draft_system_prompt = payload.draft_system_prompt
    if payload.enable_weather_api is not None:
        config.enable_weather_api = payload.enable_weather_api

    db.commit()
    db.refresh(config)
    return config

# --------------------
# FRAME TYPE ENDPOINTS
# --------------------
from app.models.administration import FrameType
from app.schemas.admin import FrameTypeCreate, FrameTypeOut
from app.models.hive import Hive, HiveBox

@router.get("/frame-types", response_model=List[FrameTypeOut])
def admin_list_frame_types(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Lists all frame types."""
    return db.query(FrameType).order_by(FrameType.name).all()

@router.post("/frame-types", response_model=FrameTypeOut, status_code=status.HTTP_201_CREATED)
def admin_create_frame_type(
    payload: FrameTypeCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Creates a new frame type."""
    # Check duplicate
    existing = db.query(FrameType).filter(FrameType.name.ilike(payload.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ein Wabenmaß mit diesem Namen existiert bereits."
        )
        
    if payload.is_default:
        db.query(FrameType).update({FrameType.is_default: False})
        
    new_ft = FrameType(
        name=payload.name,
        is_default=payload.is_default,
        brood_multiplier=payload.brood_multiplier,
        food_multiplier=payload.food_multiplier,
        bee_multiplier=payload.bee_multiplier,
        drone_multiplier=payload.drone_multiplier,
        drone_brood_multiplier=payload.drone_brood_multiplier,
        pollen_multiplier=payload.pollen_multiplier
    )
    db.add(new_ft)
    db.commit()
    db.refresh(new_ft)
    return new_ft

@router.put("/frame-types/{frame_type_id}", response_model=FrameTypeOut)
def admin_update_frame_type(
    frame_type_id: str,
    payload: FrameTypeCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Updates multipliers and default status of a frame type."""
    ft = db.query(FrameType).filter(FrameType.id == frame_type_id).first()
    if not ft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wabenmaß nicht gefunden."
        )
        
    # Check duplicate name if changed
    if payload.name.lower() != ft.name.lower():
        existing = db.query(FrameType).filter(FrameType.name.ilike(payload.name)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ein Wabenmaß mit diesem Namen existiert bereits."
            )
            
    if payload.is_default and not ft.is_default:
        db.query(FrameType).update({FrameType.is_default: False})
        
    ft.name = payload.name
    ft.is_default = payload.is_default
    ft.brood_multiplier = payload.brood_multiplier
    ft.food_multiplier = payload.food_multiplier
    ft.bee_multiplier = payload.bee_multiplier
    ft.drone_multiplier = payload.drone_multiplier
    ft.drone_brood_multiplier = payload.drone_brood_multiplier
    ft.pollen_multiplier = payload.pollen_multiplier
    
    db.commit()
    db.refresh(ft)
    return ft

@router.delete("/frame-types/{frame_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_frame_type(
    frame_type_id: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Deletes a frame type if not referenced by any hive or box."""
    ft = db.query(FrameType).filter(FrameType.id == frame_type_id).first()
    if not ft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wabenmaß nicht gefunden."
        )
        
    # Check if used by hives or boxes
    hives_count = db.query(Hive).filter(Hive.frame_type_id == frame_type_id).count()
    boxes_count = db.query(HiveBox).filter(HiveBox.frame_type_id == frame_type_id).count()
    
    if hives_count > 0 or boxes_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dieses Wabenmaß wird noch von Bienenvölkern oder Zargen verwendet und kann nicht gelöscht werden."
        )
        
    db.delete(ft)
    db.commit()
    return

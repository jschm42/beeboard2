from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserOut
from app.schemas.admin import (
    ApiKeyConfigOut,
    ApiKeyConfigUpdate,
    LLMConfigOut,
    LLMConfigUpdate,
    SMTPConfigOut,
    SMTPConfigUpdate,
    UserAdminCreate,
    UserAdminUpdate,
)
from app.services.system_settings import (
    get_api_key_status,
    get_llm_config,
    get_smtp_status,
    set_api_keys,
    set_smtp_settings,
)

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
    _current_admin: User = Depends(get_current_admin)
):
    """Lists all users in the system."""
    return db.query(User).order_by(User.username).all()


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    payload: UserAdminCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Creates a user manually (admin only)."""
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Benutzername bereits vergeben.")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-Mail-Adresse bereits vergeben.")

    role = payload.role if payload.role in {"USER", "SYSTEM_ADMIN"} else "USER"
    is_admin = role == "SYSTEM_ADMIN"

    user = User(
        username=payload.username,
        email=str(payload.email),
        hashed_password=get_password_hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=role,
        is_active=payload.is_active,
        is_staff=is_admin,
        is_superuser=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/users/{user_id}", response_model=UserOut)
def update_user_admin(
    user_id: str,
    payload: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Updates a user profile, role, active status or password (admin only, blocks self-lockout)."""
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
        if payload.role not in {"USER", "SYSTEM_ADMIN"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültige Rolle. Erlaubt sind USER oder SYSTEM_ADMIN."
            )
        user.role = payload.role
        is_admin = payload.role == "SYSTEM_ADMIN"
        user.is_staff = is_admin
        user.is_superuser = is_admin
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.username is not None and payload.username != user.username:
        existing = db.query(User).filter(User.username == payload.username, User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Benutzername bereits vergeben.")
        user.username = payload.username
    if payload.email is not None and str(payload.email) != user.email:
        existing = db.query(User).filter(User.email == str(payload.email), User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-Mail-Adresse bereits vergeben.")
        user.email = str(payload.email)
    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.password is not None and payload.password.strip():
        user.hashed_password = get_password_hash(payload.password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_admin(
    user_id: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Deletes a user (admin only), with self-protection and at-least-one-admin guard."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden.")

    if user.id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Du kannst dein eigenes Konto nicht löschen.")

    if user.role == "SYSTEM_ADMIN" or user.is_superuser:
        admin_count = db.query(User).filter((User.role == "SYSTEM_ADMIN") | (User.is_superuser.is_(True))).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mindestens ein Administrator muss im System verbleiben."
            )

    db.delete(user)
    db.commit()
    return

@router.get("/llm-config", response_model=LLMConfigOut)
def read_llm_config(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Retrieves the system-wide LLM prompts and configurations."""
    return get_llm_config(db)

@router.put("/llm-config", response_model=LLMConfigOut)
def update_llm_config(
    payload: LLMConfigUpdate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Updates the system-wide LLM prompts and weather API settings."""
    config = get_llm_config(db)

    if payload.chatbot_system_prompt is not None:
        config.chatbot_system_prompt = payload.chatbot_system_prompt
    if payload.draft_system_prompt is not None:
        config.draft_system_prompt = payload.draft_system_prompt
    if payload.enable_weather_api is not None:
        config.enable_weather_api = payload.enable_weather_api
    if payload.kleinunternehmer_regelung is not None:
        config.kleinunternehmer_regelung = payload.kleinunternehmer_regelung
    if payload.ai_insights_cron is not None:
        from app.services.cron import reschedule_insights_job
        success = reschedule_insights_job(payload.ai_insights_cron)
        if not success:
            raise HTTPException(status_code=400, detail="Ungültiges UNIX Cron-Format. Bitte 5 durch Leerzeichen getrennte Werte angeben (z.B. '0 */12 * * *').")
        config.ai_insights_cron = payload.ai_insights_cron

    db.commit()
    db.refresh(config)
    return config


@router.get("/secret-config/api-keys", response_model=ApiKeyConfigOut)
def read_api_key_config(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    return {"api_keys": get_api_key_status(db)}


@router.put("/secret-config/api-keys", response_model=ApiKeyConfigOut)
def update_api_key_config(
    payload: ApiKeyConfigUpdate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    set_api_keys(db, payload.model_dump(exclude_unset=True))
    return {"api_keys": get_api_key_status(db)}


@router.get("/secret-config/smtp", response_model=SMTPConfigOut)
def read_smtp_config(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    return get_smtp_status(db)


@router.put("/secret-config/smtp", response_model=SMTPConfigOut)
def update_smtp_config(
    payload: SMTPConfigUpdate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    set_smtp_settings(db, payload.model_dump(exclude_unset=True))
    return get_smtp_status(db)

# --------------------
# FRAME TYPE ENDPOINTS
# --------------------
from app.models.administration import FrameType
from app.schemas.admin import FrameTypeCreate, FrameTypeOut
from app.models.hive import Hive, HiveBox

@router.get("/frame-types", response_model=List[FrameTypeOut])
def admin_list_frame_types(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Lists all frame types."""
    return db.query(FrameType).order_by(FrameType.name).all()

@router.post("/frame-types", response_model=FrameTypeOut, status_code=status.HTTP_201_CREATED)
def admin_create_frame_type(
    payload: FrameTypeCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
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
    _current_admin: User = Depends(get_current_admin)
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
    _current_admin: User = Depends(get_current_admin)
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

# ----------------------
# NUMBER RANGE ENDPOINTS
# ----------------------
from app.models.administration import NumberRange
from app.schemas.admin import NumberRangeOut, NumberRangeUpdate

@router.get("/number-ranges", response_model=List[NumberRangeOut])
def admin_list_number_ranges(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Lists all number ranges."""
    return db.query(NumberRange).order_by(NumberRange.name).all()

@router.put("/number-ranges/{range_id}", response_model=NumberRangeOut)
def admin_update_number_range(
    range_id: str,
    payload: NumberRangeUpdate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Updates a number range configuration."""
    nr = db.query(NumberRange).filter(NumberRange.id == range_id).first()
    if not nr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nummernkreis nicht gefunden."
        )

    if payload.name is not None:
        nr.name = payload.name
    if payload.prefix is not None:
        nr.prefix = payload.prefix
    if payload.current_value is not None:
        nr.current_value = payload.current_value
    if payload.digits is not None:
        nr.digits = payload.digits
    if payload.is_active is not None:
        nr.is_active = payload.is_active

    db.commit()
    db.refresh(nr)
    return nr


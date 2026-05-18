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

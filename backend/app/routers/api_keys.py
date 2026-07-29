from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyOut, ApiKeyCreateResponse

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

@router.get("", response_model=List[ApiKeyOut])
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all active API keys of the authenticated user."""
    return db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True
    ).order_by(ApiKey.created_at.desc()).all()

@router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates a new API key for the authenticated user."""
    raw_key = "bb_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    
    expires_at = None
    if payload.expires_days is not None and payload.expires_days > 0:
        expires_at = datetime.now(timezone.utc) + timedelta(days=payload.expires_days)
        
    api_key = ApiKey(
        name=payload.name,
        key_hash=key_hash,
        user_id=current_user.id,
        expires_at=expires_at,
        is_active=True
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return {
        "api_key_info": api_key,
        "raw_key": raw_key
    }

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revokes/deletes an API key."""
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API-Schlüssel nicht gefunden")
        
    db.delete(api_key)
    db.commit()
    return None

import sys
import os

@router.get("/mcp-info")
def get_mcp_info(current_user: User = Depends(get_current_user)):
    """Returns absolute paths and commands needed to configure the MCP server."""
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    python_exe = sys.executable
    return {
        "command": python_exe.replace("\\", "/"),
        "args": ["-m", "app.mcp_server"],
        "cwd": backend_dir.replace("\\", "/"),
    }


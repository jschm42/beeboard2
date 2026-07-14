from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.models.user import User
from app.schemas.user import UserOut, UserCreate
from app.schemas.admin import (
    LLMConfigOut,
    LLMConfigUpdate,
    UserAdminUpdate,
    AIInsightCronJobCreate,
    AIInsightCronJobUpdate,
    AIInsightCronJobOut,
)
from app.services.ai_assistant import get_llm_config
from app.models.ai_insight import AIInsightCronJob

router = APIRouter(prefix="/admin", tags=["admin"])

VALID_AI_INSIGHT_LOG_SCOPES = {"IMKEREI", "STANDORT", "VOLK"}

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to check if the current user is a SYSTEM_ADMIN."""
    if current_user.role != "SYSTEM_ADMIN" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Zugriff verweigert. Nur Administratoren haben Zugriff auf diesen Bereich."
        )
    return current_user

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Creates a new user (admin only)."""
    # Check uniqueness
    existing_username = db.query(User).filter(User.username == payload.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benutzername bereits vergeben."
        )
    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-Mail-Adresse bereits registriert."
        )

    # Hash password
    hashed_password = get_password_hash(payload.password)

    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=payload.role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
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
    if payload.calculate_taxes is not None:
        config.calculate_taxes = payload.calculate_taxes
        config.kleinunternehmer_regelung = not payload.calculate_taxes
    elif payload.kleinunternehmer_regelung is not None:
        config.kleinunternehmer_regelung = payload.kleinunternehmer_regelung
        config.calculate_taxes = not payload.kleinunternehmer_regelung

    if payload.ai_insights_cron is not None:
        from app.services.cron import reschedule_insights_job
        success = reschedule_insights_job(payload.ai_insights_cron)
        if not success:
            raise HTTPException(status_code=400, detail="Ungültiges UNIX Cron-Format. Bitte 5 durch Leerzeichen getrennte Werte angeben (z.B. '0 */12 * * *').")
        config.ai_insights_cron = payload.ai_insights_cron
    if payload.currency is not None:
        stripped = payload.currency.strip()
        if not stripped:
            raise HTTPException(status_code=400, detail="Währung darf nicht leer sein.")
        config.currency = stripped
    if payload.tax_rates is not None:
        raw = payload.tax_rates.strip()
        try:
            rates = [float(r.strip()) for r in raw.split(",") if r.strip()]
            if not rates:
                raise ValueError("empty")
            for r in rates:
                if r < 0 or r > 100:
                    raise ValueError(f"out of range: {r}")
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="Ungültige Steuersätze. Bitte kommagetrennte positive Zahlen zwischen 0 und 100 angeben (z.B. '0.0,7.0,19.0')."
            ) from exc
        config.tax_rates = ",".join(str(r) for r in rates)

    db.commit()
    db.refresh(config)
    return config


@router.get("/ai-insight-jobs", response_model=List[AIInsightCronJobOut])
def list_ai_insight_jobs(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin),
):
    """List all configured AI-Insights cron jobs."""
    return db.query(AIInsightCronJob).order_by(AIInsightCronJob.created_at.desc()).all()


@router.post("/ai-insight-jobs", response_model=AIInsightCronJobOut, status_code=status.HTTP_201_CREATED)
def create_ai_insight_job(
    payload: AIInsightCronJobCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin),
):
    """Create a new AI-Insights cron job entry."""
    from app.services.cron import schedule_ai_insight_job

    _validate_ai_insight_log_scope(payload.log_scope)
    _validate_max_log_entries(payload.max_log_entries)

    stripped_name = payload.name.strip()
    stripped_prompt = payload.prompt.strip()
    stripped_cron = payload.cron_expression.strip()
    if not stripped_name:
        raise HTTPException(status_code=400, detail="Name darf nicht leer sein.")
    if not stripped_prompt:
        raise HTTPException(status_code=400, detail="Prompt darf nicht leer sein.")
    if not stripped_cron:
        raise HTTPException(status_code=400, detail="Cron-Ausdruck darf nicht leer sein.")

    job = AIInsightCronJob(
        name=stripped_name,
        prompt=stripped_prompt,
        cron_expression=stripped_cron,
        inject_weather=payload.inject_weather,
        inject_locations=payload.inject_locations,
        inject_apiary=payload.inject_apiary,
        inject_hives=payload.inject_hives,
        inject_log_entries=payload.inject_log_entries,
        log_scope=payload.log_scope,
        max_log_entries=payload.max_log_entries,
        is_active=payload.is_active,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    if job.is_active and not schedule_ai_insight_job(job):
        db.delete(job)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Ungültiges UNIX Cron-Format. Bitte 5 durch Leerzeichen getrennte Werte angeben (z.B. '0 */12 * * *').",
        )

    return job


@router.put("/ai-insight-jobs/{job_id}", response_model=AIInsightCronJobOut)
def update_ai_insight_job(
    job_id: str,
    payload: AIInsightCronJobUpdate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin),
):
    """Update an existing AI-Insights cron job entry."""
    from app.services.cron import schedule_ai_insight_job, remove_ai_insight_job_schedule

    job = db.query(AIInsightCronJob).filter(AIInsightCronJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="AI-Insights Job nicht gefunden.")

    if payload.name is not None:
        stripped_name = payload.name.strip()
        if not stripped_name:
            raise HTTPException(status_code=400, detail="Name darf nicht leer sein.")
        job.name = stripped_name
    if payload.prompt is not None:
        stripped_prompt = payload.prompt.strip()
        if not stripped_prompt:
            raise HTTPException(status_code=400, detail="Prompt darf nicht leer sein.")
        job.prompt = stripped_prompt
    if payload.cron_expression is not None:
        stripped_cron = payload.cron_expression.strip()
        if not stripped_cron:
            raise HTTPException(status_code=400, detail="Cron-Ausdruck darf nicht leer sein.")
        job.cron_expression = stripped_cron
    if payload.inject_weather is not None:
        job.inject_weather = payload.inject_weather
    if payload.inject_locations is not None:
        job.inject_locations = payload.inject_locations
    if payload.inject_apiary is not None:
        job.inject_apiary = payload.inject_apiary
    if payload.inject_hives is not None:
        job.inject_hives = payload.inject_hives
    if payload.inject_log_entries is not None:
        job.inject_log_entries = payload.inject_log_entries
    if payload.log_scope is not None:
        _validate_ai_insight_log_scope(payload.log_scope)
        job.log_scope = payload.log_scope
    if payload.max_log_entries is not None:
        _validate_max_log_entries(payload.max_log_entries)
        job.max_log_entries = payload.max_log_entries
    if payload.is_active is not None:
        job.is_active = payload.is_active

    db.commit()
    db.refresh(job)

    if not job.is_active:
        remove_ai_insight_job_schedule(job.id)
    else:
        if not schedule_ai_insight_job(job):
            raise HTTPException(
                status_code=400,
                detail="Ungültiges UNIX Cron-Format. Bitte 5 durch Leerzeichen getrennte Werte angeben (z.B. '0 */12 * * *').",
            )

    return job


@router.delete("/ai-insight-jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_insight_job(
    job_id: str,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin),
):
    """Delete an AI-Insights cron job entry."""
    from app.services.cron import remove_ai_insight_job_schedule

    job = db.query(AIInsightCronJob).filter(AIInsightCronJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="AI-Insights Job nicht gefunden.")

    remove_ai_insight_job_schedule(job.id)
    db.delete(job)
    db.commit()
    return


def _validate_ai_insight_log_scope(scope: str) -> None:
    if scope not in VALID_AI_INSIGHT_LOG_SCOPES:
        raise HTTPException(
            status_code=400,
            detail="Ungültiger Log-Scope. Erlaubt: IMKEREI, STANDORT, VOLK.",
        )


def _validate_max_log_entries(value: int) -> None:
    if value < 1 or value > 500:
        raise HTTPException(
            status_code=400,
            detail="Maximale Anzahl Logeinträge muss zwischen 1 und 500 liegen.",
        )

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


# -----------------------------
# TREATMENT METHOD ENDPOINTS
# -----------------------------
from app.models.treatment import TreatmentMethod, Treatment, TreatmentApplicationType
from app.schemas.treatment import (
    TreatmentMethodCreate, TreatmentMethodOut,
    TreatmentApplicationTypeCreate, TreatmentApplicationTypeOut
)

@router.get("/treatment-methods", response_model=List[TreatmentMethodOut])
def admin_list_treatment_methods(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Lists all treatment methods for admin view."""
    return db.query(TreatmentMethod).order_by(TreatmentMethod.name).all()

@router.post("/treatment-methods", response_model=TreatmentMethodOut, status_code=status.HTTP_201_CREATED)
def admin_create_treatment_method(
    payload: TreatmentMethodCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Creates a new treatment method."""
    existing = db.query(TreatmentMethod).filter(TreatmentMethod.name.ilike(payload.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Eine Behandlungsmethode mit diesem Namen existiert bereits."
        )
    
    new_method = TreatmentMethod(
        name=payload.name,
        unit=payload.unit,
        is_active=payload.is_active
    )
    db.add(new_method)
    db.commit()
    db.refresh(new_method)
    return new_method

@router.put("/treatment-methods/{method_id}", response_model=TreatmentMethodOut)
def admin_update_treatment_method(
    method_id: str,
    payload: TreatmentMethodCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Updates a treatment method's name, unit and active status."""
    method = db.query(TreatmentMethod).filter(TreatmentMethod.id == method_id).first()
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behandlungsmethode nicht gefunden."
        )
    
    if payload.name.lower() != method.name.lower():
        existing = db.query(TreatmentMethod).filter(TreatmentMethod.name.ilike(payload.name)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Eine Behandlungsmethode mit diesem Namen existiert bereits."
            )
            
    method.name = payload.name
    method.unit = payload.unit
    method.is_active = payload.is_active
    
    db.commit()
    db.refresh(method)
    return method

@router.delete("/treatment-methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_treatment_method(
    method_id: str,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Deletes a treatment method if not referenced by any treatment record."""
    method = db.query(TreatmentMethod).filter(TreatmentMethod.id == method_id).first()
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behandlungsmethode nicht gefunden."
        )
        
    # Check if referenced by any treatment record
    used_count = db.query(Treatment).filter(Treatment.treatment_method_id == method_id).count()
    if used_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Diese Behandlungsmethode wird noch von aufgezeichneten Behandlungen verwendet und kann nicht gelöscht werden."
        )
        
    db.delete(method)
    db.commit()
    return

@router.get("/treatment-application-types", response_model=List[TreatmentApplicationTypeOut])
def admin_list_treatment_application_types(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Lists all treatment application types for admin view."""
    return db.query(TreatmentApplicationType).order_by(TreatmentApplicationType.name).all()

@router.post("/treatment-application-types", response_model=TreatmentApplicationTypeOut, status_code=status.HTTP_201_CREATED)
def admin_create_treatment_application_type(
    payload: TreatmentApplicationTypeCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Creates a new treatment application type."""
    existing = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.name.ilike(payload.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Eine Applikationsmethode mit diesem Namen existiert bereits."
        )
    
    new_app = TreatmentApplicationType(
        name=payload.name,
        is_active=payload.is_active
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

@router.put("/treatment-application-types/{app_id}", response_model=TreatmentApplicationTypeOut)
def admin_update_treatment_application_type(
    app_id: str,
    payload: TreatmentApplicationTypeCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Updates a treatment application type's name and active status."""
    app_type = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.id == app_id).first()
    if not app_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applikationsmethode nicht gefunden."
        )
    
    if payload.name.lower() != app_type.name.lower():
        existing = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.name.ilike(payload.name)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Eine Applikationsmethode mit diesem Namen existiert bereits."
            )
            
    app_type.name = payload.name
    app_type.is_active = payload.is_active
    
    db.commit()
    db.refresh(app_type)
    return app_type

@router.delete("/treatment-application-types/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_treatment_application_type(
    app_id: str,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin)
):
    """Deletes a treatment application type if not referenced by any treatment record."""
    app_type = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.id == app_id).first()
    if not app_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applikationsmethode nicht gefunden."
        )
        
    # Check if referenced by any treatment record
    used_count = db.query(Treatment).filter(Treatment.application_type_id == app_id).count()
    if used_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Diese Applikationsmethode wird noch von aufgezeichneten Behandlungen verwendet und kann nicht gelöscht werden."
        )
        
    db.delete(app_type)
    db.commit()
    return



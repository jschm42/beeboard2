"""
Bee-Agent Router

CRUD endpoints for BeeAgentJob configuration and BeeAgentProposal management.
"""
import json
import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.bee_agent import BeeAgentJob, BeeAgentProposal
from app.models.task import Task
from app.models.user import User
from app.routers.apiaries import check_access

logger = logging.getLogger("beeboard.bee_agent")

router = APIRouter(prefix="/bee-agent", tags=["bee-agent"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class BeeAgentJobCreate(BaseModel):
    name: str
    custom_prompt: Optional[str] = None
    scope: str = "IMKEREI"
    entity_ids: Optional[List[str]] = None
    include_weather_data: bool = False
    include_journal_entries: bool = True
    max_journal_entries: Optional[int] = None
    cron_expression: str = "0 8 * * *"
    is_active: bool = True
    execution_mode: str = "SUGGESTION"


class BeeAgentJobUpdate(BaseModel):
    name: Optional[str] = None
    custom_prompt: Optional[str] = None
    scope: Optional[str] = None
    entity_ids: Optional[List[str]] = None
    include_weather_data: Optional[bool] = None
    include_journal_entries: Optional[bool] = None
    max_journal_entries: Optional[int] = None
    cron_expression: Optional[str] = None
    is_active: Optional[bool] = None
    execution_mode: Optional[str] = None


class BeeAgentJobOut(BaseModel):
    id: str
    apiary_id: Optional[str]
    name: str
    custom_prompt: Optional[str]
    scope: str
    entity_ids: Optional[List[str]]
    include_weather_data: bool
    include_journal_entries: bool
    max_journal_entries: Optional[int]
    cron_expression: str
    is_active: bool
    execution_mode: str
    created_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, job: BeeAgentJob) -> "BeeAgentJobOut":
        entity_ids_parsed: Optional[List[str]] = None
        if job.entity_ids:
            try:
                entity_ids_parsed = json.loads(job.entity_ids)
            except (ValueError, TypeError):
                entity_ids_parsed = None
        return cls(
            id=job.id,
            apiary_id=job.apiary_id,
            name=job.name,
            custom_prompt=job.custom_prompt,
            scope=job.scope,
            entity_ids=entity_ids_parsed,
            include_weather_data=job.include_weather_data,
            include_journal_entries=job.include_journal_entries,
            max_journal_entries=job.max_journal_entries,
            cron_expression=job.cron_expression,
            is_active=job.is_active,
            execution_mode=job.execution_mode,
            created_at=job.created_at.isoformat(),
        )


class BeeAgentProposalOut(BaseModel):
    id: str
    job_id: Optional[str]
    apiary_id: str
    title: str
    description: Optional[str]
    priority: str
    due_date: Optional[str]
    location_id: Optional[str]
    hive_id: Optional[str]
    is_accepted: bool
    created_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, p: BeeAgentProposal) -> "BeeAgentProposalOut":
        return cls(
            id=p.id,
            job_id=p.job_id,
            apiary_id=p.apiary_id,
            title=p.title,
            description=p.description,
            priority=p.priority,
            due_date=p.due_date.isoformat() if p.due_date else None,
            location_id=p.location_id,
            hive_id=p.hive_id,
            is_accepted=p.is_accepted,
            created_at=p.created_at.isoformat(),
        )


# ---------------------------------------------------------------------------
# Job endpoints
# ---------------------------------------------------------------------------

@router.get("/jobs", response_model=List[BeeAgentJobOut])
def list_jobs(
    apiary_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists all Bee-Agent jobs for an apiary."""
    check_access(apiary_id, current_user, db)
    jobs = db.query(BeeAgentJob).filter(BeeAgentJob.apiary_id == apiary_id).all()
    return [BeeAgentJobOut.from_orm_model(j) for j in jobs]


@router.post("/jobs", response_model=BeeAgentJobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: BeeAgentJobCreate,
    apiary_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a new Bee-Agent job configuration."""
    check_access(apiary_id, current_user, db)
    _validate_scope(payload.scope)
    _validate_execution_mode(payload.execution_mode)

    job = BeeAgentJob(
        apiary_id=apiary_id,
        created_by_id=current_user.id,
        name=payload.name,
        custom_prompt=payload.custom_prompt,
        scope=payload.scope,
        entity_ids=json.dumps(payload.entity_ids) if payload.entity_ids is not None else None,
        include_weather_data=payload.include_weather_data,
        include_journal_entries=payload.include_journal_entries,
        max_journal_entries=payload.max_journal_entries,
        cron_expression=payload.cron_expression,
        is_active=payload.is_active,
        execution_mode=payload.execution_mode,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    _sync_job_schedule(job)

    return BeeAgentJobOut.from_orm_model(job)


@router.put("/jobs/{job_id}", response_model=BeeAgentJobOut)
def update_job(
    job_id: str,
    payload: BeeAgentJobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates a Bee-Agent job configuration."""
    job = _get_job_or_404(job_id, db)
    check_access(job.apiary_id, current_user, db)

    if payload.scope is not None:
        _validate_scope(payload.scope)
        job.scope = payload.scope
    if payload.execution_mode is not None:
        _validate_execution_mode(payload.execution_mode)
        job.execution_mode = payload.execution_mode
    if payload.name is not None:
        job.name = payload.name
    if payload.custom_prompt is not None:
        job.custom_prompt = payload.custom_prompt
    if payload.entity_ids is not None:
        job.entity_ids = json.dumps(payload.entity_ids)
    if payload.include_weather_data is not None:
        job.include_weather_data = payload.include_weather_data
    if payload.include_journal_entries is not None:
        job.include_journal_entries = payload.include_journal_entries
    if payload.max_journal_entries is not None:
        job.max_journal_entries = payload.max_journal_entries
    if payload.cron_expression is not None:
        job.cron_expression = payload.cron_expression
    if payload.is_active is not None:
        job.is_active = payload.is_active

    db.commit()
    db.refresh(job)

    _sync_job_schedule(job)

    return BeeAgentJobOut.from_orm_model(job)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a Bee-Agent job and its associated proposals."""
    job = _get_job_or_404(job_id, db)
    check_access(job.apiary_id, current_user, db)

    _remove_job_schedule(job_id)

    db.delete(job)
    db.commit()
    return


@router.post("/jobs/{job_id}/trigger", response_model=dict)
async def trigger_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually triggers a single Bee-Agent job run."""
    job = _get_job_or_404(job_id, db)
    check_access(job.apiary_id, current_user, db)

    from app.services.cron import run_bee_agent_job_queued
    await run_bee_agent_job_queued(job_id)
    return {"status": "success", "message": f"Job '{job.name}' wurde ausgeführt."}


# ---------------------------------------------------------------------------
# Proposal endpoints
# ---------------------------------------------------------------------------

@router.get("/proposals", response_model=List[BeeAgentProposalOut])
def list_proposals(
    apiary_id: str = Query(...),
    job_id: Optional[str] = Query(None),
    is_accepted: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists Bee-Agent proposals for an apiary."""
    check_access(apiary_id, current_user, db)
    query = db.query(BeeAgentProposal).filter(BeeAgentProposal.apiary_id == apiary_id)
    if job_id:
        query = query.filter(BeeAgentProposal.job_id == job_id)
    if is_accepted is not None:
        query = query.filter(BeeAgentProposal.is_accepted == is_accepted)
    proposals = query.order_by(BeeAgentProposal.created_at.desc()).all()
    return [BeeAgentProposalOut.from_orm_model(p) for p in proposals]


@router.delete("/proposals/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a proposal."""
    proposal = _get_proposal_or_404(proposal_id, db)
    check_access(proposal.apiary_id, current_user, db)
    db.delete(proposal)
    db.commit()
    return


@router.post("/proposals/{proposal_id}/accept", response_model=dict)
def accept_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accepts a proposal and creates a corresponding Task in the database."""
    proposal = _get_proposal_or_404(proposal_id, db)
    check_access(proposal.apiary_id, current_user, db)

    if proposal.is_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dieser Vorschlag wurde bereits akzeptiert."
        )

    new_task = Task(
        title=proposal.title,
        description=proposal.description,
        due_date=proposal.due_date,
        priority=proposal.priority,
        location_id=proposal.location_id,
        hive_id=proposal.hive_id,
        is_recurring=False,
        apiary_id=proposal.apiary_id,
        created_by_id=current_user.id,
        is_completed=False,
    )
    db.add(new_task)

    proposal.is_accepted = True
    db.commit()
    db.refresh(new_task)

    return {"status": "success", "task_id": new_task.id}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_job_or_404(job_id: str, db: Session) -> BeeAgentJob:
    job = db.query(BeeAgentJob).filter(BeeAgentJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Bee-Agent Job nicht gefunden.")
    return job


def _get_proposal_or_404(proposal_id: str, db: Session) -> BeeAgentProposal:
    proposal = db.query(BeeAgentProposal).filter(BeeAgentProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Vorschlag nicht gefunden.")
    return proposal


def _validate_scope(scope: str) -> None:
    if scope not in ("IMKEREI", "STANDORT", "VOLK"):
        raise HTTPException(
            status_code=400,
            detail="Ungültiger Scope. Erlaubt: IMKEREI, STANDORT, VOLK."
        )


def _validate_execution_mode(mode: str) -> None:
    if mode not in ("SUGGESTION", "AUTO_CREATE"):
        raise HTTPException(
            status_code=400,
            detail="Ungültiger Execution-Mode. Erlaubt: SUGGESTION, AUTO_CREATE."
        )


def _sync_job_schedule(job: BeeAgentJob) -> None:
    """Adds or removes the APScheduler job based on is_active flag."""
    try:
        from app.services.cron import schedule_bee_agent_job, remove_bee_agent_job_schedule
        if job.is_active:
            schedule_bee_agent_job(job)
        else:
            remove_bee_agent_job_schedule(job.id)
    except Exception as e:
        logger.warning(f"Could not sync schedule for job {job.id}: {e}")


def _remove_job_schedule(job_id: str) -> None:
    try:
        from app.services.cron import remove_bee_agent_job_schedule
        remove_bee_agent_job_schedule(job_id)
    except Exception as e:
        logger.warning(f"Could not remove schedule for job {job_id}: {e}")

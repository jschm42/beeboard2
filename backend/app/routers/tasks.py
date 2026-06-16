from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional
import calendar

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.routers.apiaries import check_access

router = APIRouter(prefix="/tasks", tags=["tasks"])


def calculate_next_due_date(current_due_date: Optional[date], interval: str) -> date:
    if not current_due_date:
        current_due_date = date.today()
    
    interval = interval.upper()
    if interval == "DAILY":
        return current_due_date + timedelta(days=1)
    elif interval == "WEEKLY":
        return current_due_date + timedelta(weeks=1)
    elif interval == "BIWEEKLY":
        return current_due_date + timedelta(weeks=2)
    elif interval.startswith("EVERY_") and interval.endswith("_DAYS"):
        try:
            days = int(interval.split("_")[1])
            return current_due_date + timedelta(days=days)
        except (IndexError, ValueError):
            return current_due_date + timedelta(weeks=1)
    elif interval == "MONTHLY":
        year = current_due_date.year
        month = current_due_date.month + 1
        if month > 12:
            month = 1
            year += 1
        day = current_due_date.day
        last_day = calendar.monthrange(year, month)[1]
        if day > last_day:
            day = last_day
        return date(year, month, day)
    elif interval == "YEARLY":
        year = current_due_date.year + 1
        month = current_due_date.month
        day = current_due_date.day
        last_day = calendar.monthrange(year, month)[1]
        if day > last_day:
            day = last_day
        return date(year, month, day)
    else:
        return current_due_date + timedelta(weeks=1)


@router.get("", response_model=List[TaskOut])
def list_tasks(
    apiary_id: str = Query(..., description="Scope search to a specific apiary"),
    location_id: Optional[str] = Query(None),
    hive_id: Optional[str] = Query(None),
    is_completed: Optional[bool] = Query(None),
    priority: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all tasks for an authorized apiary, with optional filters."""
    check_access(apiary_id, current_user, db)
    
    query = db.query(Task).options(
        joinedload(Task.location),
        joinedload(Task.hive)
    ).filter(Task.apiary_id == apiary_id)
    
    if location_id:
        query = query.filter(Task.location_id == location_id)
    if hive_id:
        query = query.filter(Task.hive_id == hive_id)
    if is_completed is not None:
        query = query.filter(Task.is_completed == is_completed)
    if priority:
        query = query.filter(Task.priority == priority)
    if start_date:
        query = query.filter(Task.due_date >= start_date)
    if end_date:
        query = query.filter(Task.due_date <= end_date)
        
    return query.order_by(Task.is_completed.asc(), Task.due_date.asc(), Task.created_at.desc()).all()


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    apiary_id: str = Query(..., description="Scope creation to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new task in an authorized apiary."""
    check_access(apiary_id, current_user, db)
    
    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        priority=task_in.priority,
        location_id=task_in.location_id if task_in.location_id else None,
        hive_id=task_in.hive_id if task_in.hive_id else None,
        is_recurring=task_in.is_recurring,
        recurrence_interval=task_in.recurrence_interval if task_in.is_recurring else None,
        apiary_id=apiary_id,
        created_by_id=current_user.id,
        is_completed=False
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # Reload relationships
    return db.query(Task).options(
        joinedload(Task.location),
        joinedload(Task.hive)
    ).filter(Task.id == new_task.id).first()


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: str,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates a task's details and manages completion triggers."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aufgabe nicht gefunden")
        
    check_access(task.apiary_id, current_user, db)
    
    was_completed = task.is_completed
    
    if task_in.title is not None:
        task.title = task_in.title
    if task_in.description is not None:
        task.description = task_in.description
    if task_in.due_date is not None:
        task.due_date = task_in.due_date
    if task_in.priority is not None:
        task.priority = task_in.priority
    if task_in.location_id is not None:
        task.location_id = task_in.location_id if task_in.location_id else None
    if task_in.hive_id is not None:
        task.hive_id = task_in.hive_id if task_in.hive_id else None
    if task_in.is_recurring is not None:
        task.is_recurring = task_in.is_recurring
        if not task_in.is_recurring:
            task.recurrence_interval = None
    if task_in.recurrence_interval is not None:
        task.recurrence_interval = task_in.recurrence_interval if task.is_recurring else None
    if task_in.is_completed is not None:
        task.is_completed = task_in.is_completed
        if task_in.is_completed:
            if not task.completed_at:
                task.completed_at = datetime.now(timezone.utc)
        else:
            task.completed_at = None
            
    db.commit()
    db.refresh(task)
    
    # Recurrence trigger
    if not was_completed and task.is_completed and task.is_recurring and task.recurrence_interval:
        next_due = calculate_next_due_date(task.due_date, task.recurrence_interval)
        new_task = Task(
            title=task.title,
            description=task.description,
            due_date=next_due,
            priority=task.priority,
            is_completed=False,
            location_id=task.location_id,
            hive_id=task.hive_id,
            is_recurring=True,
            recurrence_interval=task.recurrence_interval,
            apiary_id=task.apiary_id,
            created_by_id=current_user.id
        )
        db.add(new_task)
        db.commit()
        
    return db.query(Task).options(
        joinedload(Task.location),
        joinedload(Task.hive)
    ).filter(Task.id == task_id).first()


@router.post("/{task_id}/complete", response_model=TaskOut)
def complete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks a task as completed and generates the next recurring instance if configured."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aufgabe nicht gefunden")
        
    check_access(task.apiary_id, current_user, db)
    
    if not task.is_completed:
        task.is_completed = True
        task.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
        
        # Recurrence logic
        if task.is_recurring and task.recurrence_interval:
            next_due = calculate_next_due_date(task.due_date, task.recurrence_interval)
            new_task = Task(
                title=task.title,
                description=task.description,
                due_date=next_due,
                priority=task.priority,
                is_completed=False,
                location_id=task.location_id,
                hive_id=task.hive_id,
                is_recurring=True,
                recurrence_interval=task.recurrence_interval,
                apiary_id=task.apiary_id,
                created_by_id=current_user.id
            )
            db.add(new_task)
            db.commit()
            
    return db.query(Task).options(
        joinedload(Task.location),
        joinedload(Task.hive)
    ).filter(Task.id == task_id).first()


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aufgabe nicht gefunden")
        
    check_access(task.apiary_id, current_user, db, require_admin=True)
    
    db.delete(task)
    db.commit()
    return

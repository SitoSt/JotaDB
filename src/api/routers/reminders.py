"""
Router para operaciones CRUD de Reminders (Recordatorios).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from src.core.database import get_session
from src.core.models import Reminder
from src.api.utils import apply_optimistic_locking, update_entity_fields, increment_version

router = APIRouter(
    prefix="/reminders",
    tags=["Reminders"],
    responses={404: {"description": "Reminder not found"}}
)


@router.post("", response_model=Reminder, status_code=status.HTTP_201_CREATED)
def create_reminder(reminder: Reminder, session: Session = Depends(get_session)):
    """Crear un nuevo recordatorio"""
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    return reminder


@router.get("", response_model=List[Reminder])
def read_reminders(
    is_completed: Optional[bool] = None,
    task_id: Optional[int] = None,
    event_id: Optional[int] = None,
    trigger_after: Optional[datetime] = None,
    trigger_before: Optional[datetime] = None,
    session: Session = Depends(get_session)
):
    """Listar todos los recordatorios con filtros opcionales"""
    query = select(Reminder)
    
    if is_completed is not None:
        query = query.where(Reminder.is_completed == is_completed)
    if task_id:
        query = query.where(Reminder.task_id == task_id)
    if event_id:
        query = query.where(Reminder.event_id == event_id)
    if trigger_after:
        query = query.where(Reminder.trigger_at >= trigger_after)
    if trigger_before:
        query = query.where(Reminder.trigger_at <= trigger_before)
    
    reminders = session.exec(query).all()
    return reminders


@router.get("/{reminder_id}", response_model=Reminder)
def read_reminder(reminder_id: int, session: Session = Depends(get_session)):
    """Obtener un recordatorio específico por ID"""
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.patch("/{reminder_id}", response_model=Reminder)
def update_reminder(
    reminder_id: int,
    reminder_update: dict,
    session: Session = Depends(get_session)
):
    """
    Actualizar un recordatorio existente con optimistic locking.
    Requiere enviar el campo 'version' actual para prevenir conflictos.
    """
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Aplicar optimistic locking
    apply_optimistic_locking(reminder, reminder_update)
    
    # Actualizar campos
    update_entity_fields(reminder, reminder_update)
    
    # Incrementar versión y timestamp
    increment_version(reminder)
    
    session.add(reminder)
    session.commit()
    session.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: int, session: Session = Depends(get_session)):
    """Eliminar un recordatorio"""
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    session.delete(reminder)
    session.commit()
    return None

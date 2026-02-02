"""
Router para operaciones CRUD de Events (Eventos).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from src.core.database import get_session
from src.core.models import Event
from src.api.utils import apply_optimistic_locking, update_entity_fields, increment_version

router = APIRouter(
    prefix="/events",
    tags=["Events"],
    responses={404: {"description": "Event not found"}}
)


@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: Event, session: Session = Depends(get_session)):
    """Crear un nuevo evento"""
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.get("", response_model=List[Event])
def read_events(
    start_after: Optional[datetime] = None,
    start_before: Optional[datetime] = None,
    all_day: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    """Listar todos los eventos con filtros opcionales"""
    query = select(Event)
    
    if start_after:
        query = query.where(Event.start_at >= start_after)
    if start_before:
        query = query.where(Event.start_at <= start_before)
    if all_day is not None:
        query = query.where(Event.all_day == all_day)
    
    events = session.exec(query).all()
    return events


@router.get("/{event_id}", response_model=Event)
def read_event(event_id: int, session: Session = Depends(get_session)):
    """Obtener un evento específico por ID"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/{event_id}", response_model=Event)
def update_event(
    event_id: int,
    event_update: dict,
    session: Session = Depends(get_session)
):
    """
    Actualizar un evento existente con optimistic locking.
    Requiere enviar el campo 'version' actual para prevenir conflictos.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Aplicar optimistic locking
    apply_optimistic_locking(event, event_update)
    
    # Actualizar campos
    update_entity_fields(event, event_update)
    
    # Incrementar versión y timestamp
    increment_version(event)
    
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, session: Session = Depends(get_session)):
    """Eliminar un evento"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    session.delete(event)
    session.commit()
    return None

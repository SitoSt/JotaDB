"""
Router para operaciones CRUD de Tasks (Tareas).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional

from src.core.database import get_session
from src.core.models import Task
from src.api.utils import apply_optimistic_locking, update_entity_fields, increment_version

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={404: {"description": "Task not found"}}
)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: Task, session: Session = Depends(get_session)):
    """Crear una nueva tarea"""
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("", response_model=List[Task])
def read_tasks(
    status_filter: Optional[str] = None,
    priority: Optional[int] = None,
    event_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """Listar todas las tareas con filtros opcionales"""
    query = select(Task)
    
    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority:
        query = query.where(Task.priority == priority)
    if event_id:
        query = query.where(Task.event_id == event_id)
    
    tasks = session.exec(query).all()
    return tasks


@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, session: Session = Depends(get_session)):
    """Obtener una tarea específica por ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: dict,
    session: Session = Depends(get_session)
):
    """
    Actualizar una tarea existente con optimistic locking.
    Requiere enviar el campo 'version' actual para prevenir conflictos.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Aplicar optimistic locking
    apply_optimistic_locking(task, task_update)
    
    # Actualizar campos
    update_entity_fields(task, task_update)
    
    # Incrementar versión y timestamp
    increment_version(task)
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    """Eliminar una tarea"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    session.delete(task)
    session.commit()
    return None

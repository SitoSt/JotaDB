from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# --- CLASE BASE (Para no repetir campos en todas las tablas) ---
class BaseUUIDModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Versionado optimista para prevenir conflictos de escritura concurrente
    version: int = Field(default=1)

# --- EVENTOS ---
class Event(BaseUUIDModel, table=True):
    title: str
    description: Optional[str] = None
    start_at: datetime
    # end_at puede ser None (indeterminado)
    end_at: Optional[datetime] = None
    all_day: bool = False
    location: Optional[str] = None
    
    # Relación: Un evento puede tener muchas tareas
    tasks: List["Task"] = Relationship(back_populates="event")
    # Relación: Un evento puede tener muchos recordatorios
    reminders: List["Reminder"] = Relationship(back_populates="event")

# --- TAREAS ---
class Task(BaseUUIDModel, table=True):
    title: str
    status: str = Field(default="pending") # pending, doing, done
    priority: int = Field(default=1) # 1 (Baja) a 5 (Crítica)
    
    # Vinculación con Eventos (Opcional)
    event_id: Optional[int] = Field(default=None, foreign_key="event.id")
    event: Optional[Event] = Relationship(back_populates="tasks")
    
    # Campo para definir CUÁNDO se hace la tarea respecto al evento
    # Ej: "before", "during", "after"
    timing_relative_to_event: Optional[str] = None 

    # Relación: Una tarea puede tener muchos recordatorios
    reminders: List["Reminder"] = Relationship(back_populates="task")

# --- RECORDATORIOS ---
class Reminder(BaseUUIDModel, table=True):
    message: str
    trigger_at: datetime
    is_completed: bool = False
    
    # Opcionalmente vinculado a una tarea
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    task: Optional[Task] = Relationship(back_populates="reminders")
    
    # Opcionalmente vinculado directamente a un evento
    event_id: Optional[int] = Field(default=None, foreign_key="event.id")
    event: Optional[Event] = Relationship(back_populates="reminders")
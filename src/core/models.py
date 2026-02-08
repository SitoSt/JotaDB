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

# --- INFERENCE LAYER (Internal System) ---
class InferenceClient(BaseUUIDModel, table=True):
    client_id: str = Field(unique=True, index=True) # Identificador del servicio (ej: "JotaOrchestrator")
    api_key: str # Clave secreta
    role: str = Field(default="user") # admin, user
    max_sessions: int = Field(default=1)
    is_active: bool = Field(default=True)

class InferenceSession(BaseUUIDModel, table=True):
    session_id: str = Field(unique=True, index=True) # ID generado por C++
    status: str = Field(default="active") # active, closed, error
    context_summary: Optional[str] = None
    
    # Foreign Key to InferenceClient
    client_db_id: int = Field(foreign_key="inferenceclient.id")
    client: InferenceClient = Relationship()

# --- CHAT LAYER (User Facing) ---
class Client(BaseUUIDModel, table=True):
    name: str
    client_key: str = Field(unique=True, index=True) # La llave que enviará JotaDesktop
    is_active: bool = Field(default=True)
    max_concurrent_sessions: int = Field(default=1)
    
    # Relación: Un cliente puede tener muchas conversaciones
    conversations: List["Conversation"] = Relationship(back_populates="client")

class Conversation(BaseUUIDModel, table=True):
    title: Optional[str] = None
    status: str = Field(default="active") # active, archived
    
    # Vinculación con Client
    client_id: int = Field(foreign_key="client.id")
    client: Client = Relationship(back_populates="conversations")
    
    # Vinculación opcional con InferenceSession (Loose coupling)
    inference_session_id: Optional[str] = None 
    
    # Relación: Una conversación tiene muchos mensajes
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(BaseUUIDModel, table=True):
    content: str
    role: str # user, assistant, system
    
    # Vinculación con Conversation
    conversation_id: int = Field(foreign_key="conversation.id")
    conversation: Conversation = Relationship(back_populates="messages")
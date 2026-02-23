from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

from src.core.database import get_session
from src.core.models import Conversation, Message, Client, InferenceSession
from src.api.dependencies import get_current_client
from src.api.security import verify_api_key

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}}
)

# --- DTOs ---
class ConversationCreate(BaseModel):
    title: Optional[str] = None

class SessionLink(BaseModel):
    conversation_id: int
    inference_session_id: str

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageCreate(BaseModel):
    role: MessageRole
    content: str

# --- Endpoints ---

@router.post("/conversation", response_model=Conversation, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conv_data: ConversationCreate, 
    session: Session = Depends(get_session),
    client: Client = Depends(get_current_client),
    _: bool = Depends(verify_api_key)
):
    """Crea una nueva conversación para un cliente autenticado"""
    # El cliente ya viene validado por get_current_client

    conversation = Conversation(
        client_id=client.id,
        title=conv_data.title
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation

@router.get("/history/{conversation_id}", response_model=List[Message])
def get_conversation_history(
    conversation_id: int, 
    session: Session = Depends(get_session),
    client: Client = Depends(get_current_client),
    _: bool = Depends(verify_api_key)
):
    """Obtiene el historial de mensajes de una conversación"""
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    # Verificar propiedad
    if conversation.client_id != client.id:
         raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        
    # Usar query explícita para asegurar orden si es necesario, 
    # aunque la relación back_populates debería traerlos.
    # Por defecto BaseUUIDModel tiene created_at, ordenamos por eso.
    statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    messages = session.exec(statement).all()
    return messages

@router.patch("/session", response_model=Conversation)
def link_inference_session(
    link_data: SessionLink,
    session: Session = Depends(get_session),
    client: Client = Depends(get_current_client),
    _: bool = Depends(verify_api_key)
):
    """Vincula una Conversation con una InferenceSession activa"""
    conversation = session.get(Conversation, link_data.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Verificar propiedad
    if conversation.client_id != client.id:
         raise HTTPException(status_code=403, detail="Not authorized to modify this conversation")
    
    # Validar que la sesión de inferencia exista (Opcional)
    # Ya que The Orchestrator es un servicio de confianza y el motor de C++ 
    # actualmente no inserta InferenceSession en la BD, nos saltamos la validación estricta.

    conversation.inference_session_id = link_data.inference_session_id
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation

@router.post("/{conversation_id}/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    session: Session = Depends(get_session),
    client: Client = Depends(get_current_client),
    _: bool = Depends(verify_api_key)
):
    """Agrega un mensaje a una conversación"""
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    # Verificar propiedad
    if conversation.client_id != client.id:
         raise HTTPException(status_code=403, detail="Not authorized to post to this conversation")

    message = Message(
        conversation_id=conversation_id,
        role=message_data.role.value,
        content=message_data.content
    )
    
    # Actualizar timestamp de la conversación
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

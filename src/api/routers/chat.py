from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.core.database import get_session
from src.core.models import Conversation, Message, Client, InferenceSession

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}}
)

# --- DTOs ---
class ConversationCreate(BaseModel):
    client_id: int
    title: Optional[str] = None

class SessionLink(BaseModel):
    conversation_id: int
    inference_session_id: str

class MessageCreate(BaseModel):
    role: str
    content: str

# --- Endpoints ---

@router.post("/conversation", response_model=Conversation, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conv_data: ConversationCreate, 
    session: Session = Depends(get_session)
):
    """Crea una nueva conversación para un cliente"""
    # Verificar que el cliente existe
    client = session.get(Client, conv_data.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    conversation = Conversation(
        client_id=conv_data.client_id,
        title=conv_data.title
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation

@router.get("/history/{conversation_id}", response_model=List[Message])
def get_conversation_history(
    conversation_id: int, 
    session: Session = Depends(get_session)
):
    """Obtiene el historial de mensajes de una conversación"""
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    # Usar query explícita para asegurar orden si es necesario, 
    # aunque la relación back_populates debería traerlos.
    # Por defecto BaseUUIDModel tiene created_at, ordenamos por eso.
    statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    messages = session.exec(statement).all()
    return messages

@router.patch("/session", response_model=Conversation)
def link_inference_session(
    link_data: SessionLink,
    session: Session = Depends(get_session)
):
    """Vincula una Conversation con una InferenceSession activa"""
    conversation = session.get(Conversation, link_data.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Validar que la sesión de inferencia exista (Opcional, pero recomendado)
    # Nota: El user dijo "InferenceSession: Seguimiento del motor de C++", 
    # session_id es un string único en InferenceSession.
    statement = select(InferenceSession).where(InferenceSession.session_id == link_data.inference_session_id)
    inf_session = session.exec(statement).first()
    
    if not inf_session:
        # Podríamos permitirlo si se confía en el orquestador, pero mejor validar.
        raise HTTPException(status_code=404, detail="Inference Session not found")

    conversation.inference_session_id = link_data.inference_session_id
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation

@router.post("/{conversation_id}/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    session: Session = Depends(get_session)
):
    """Agrega un mensaje a una conversación"""
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    message = Message(
        conversation_id=conversation_id,
        role=message_data.role,
        content=message_data.content
    )
    
    # Actualizar timestamp de la conversación
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

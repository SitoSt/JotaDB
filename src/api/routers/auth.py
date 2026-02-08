from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Optional

from src.core.database import get_session
from src.core.models import InferenceClient, Client

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}}
)

@router.get("/internal", response_model=InferenceClient)
def validate_internal_client(
    client_id: str = Query(..., description="Service Identifier"),
    api_key: str = Query(..., description="Service API Key"),
    session: Session = Depends(get_session)
):
    """
    Valida un servicio interno (ej: JotaOrchestrator) para permitir el uso del motor de C++.
    """
    statement = select(InferenceClient).where(InferenceClient.client_id == client_id)
    client = session.exec(statement).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Client not found"
        )
        
    # TODO: Implementar hash comparison seguro. Por ahora texto plano según requisitos.
    if client.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid API Key"
        )
        
    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Client is inactive"
        )
        
    return client

@router.get("/client", response_model=Client)
def validate_external_client(
    client_key: str = Query(..., description="Desktop Client Key"),
    session: Session = Depends(get_session)
):
    """
    Valida un cliente externo (ej: JotaDesktop) para permitir la conexión al Orquestador.
    """
    statement = select(Client).where(Client.client_key == client_key)
    client = session.exec(statement).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Client not found"
        )
        
    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Client is inactive"
        )
        
    return client

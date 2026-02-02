"""
Utilidades compartidas para la API.
Incluye funciones de optimistic locking y helpers comunes.
"""
from fastapi import HTTPException
from datetime import datetime
from sqlmodel import Session


def apply_optimistic_locking(entity, update_data: dict) -> None:
    """
    Aplica optimistic locking a una entidad.
    
    Args:
        entity: La entidad SQLModel a actualizar
        update_data: Diccionario con los datos de actualización
        
    Raises:
        HTTPException: Si hay un conflicto de versión (HTTP 409)
    """
    if "version" in update_data:
        if entity.version != update_data["version"]:
            raise HTTPException(
                status_code=409,
                detail=f"Version conflict: expected {entity.version}, got {update_data['version']}"
            )
        # Remover version del update ya que la incrementaremos automáticamente
        update_data.pop("version")


def update_entity_fields(entity, update_data: dict, exclude_fields: list = None) -> None:
    """
    Actualiza los campos de una entidad con los datos proporcionados.
    
    Args:
        entity: La entidad a actualizar
        update_data: Diccionario con los nuevos valores
        exclude_fields: Lista de campos que no deben ser actualizados
    """
    if exclude_fields is None:
        exclude_fields = ["id", "created_at"]
    
    for key, value in update_data.items():
        if hasattr(entity, key) and key not in exclude_fields:
            setattr(entity, key, value)


def increment_version(entity) -> None:
    """
    Incrementa la versión de una entidad y actualiza el timestamp.
    
    Args:
        entity: La entidad a actualizar
    """
    entity.version += 1
    entity.updated_at = datetime.utcnow()

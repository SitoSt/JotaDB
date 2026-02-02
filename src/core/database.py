import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:pass@db:5432/brain")

# Configuración del engine con pool robusto para acceso concurrente
# Esto permite que múltiples servicios (API + futuro MCP) accedan sin conflictos
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,        # Verifica conexiones antes de usarlas
    pool_size=10,               # Conexiones base en el pool
    max_overflow=20,            # Conexiones adicionales bajo carga
    pool_timeout=30,            # Segundos de espera antes de fallar
    pool_recycle=3600,          # Recicla conexiones cada hora (evita conexiones obsoletas)
)

def init_db():
    """
    Inicializa la base de datos: crea las tablas si no existen.
    Incluye lógica de reintento robusta.
    """
    retries = 5
    while retries > 0:
        try:
            print(f"🔄 Intentando conectar a la DB... (Reintentos restantes: {retries})")
            # Importamos los modelos aquí para evitar importaciones circulares
            from src.core import models 
            
            # Crea todas las tablas definidas en models.py
            SQLModel.metadata.create_all(engine)
            print("✅ Base de datos conectada y tablas creadas con éxito.")
            break
        except OperationalError as e:
            retries -= 1
            print(f"⚠️ La DB no está lista aún. Esperando 3 segundos... (Error: {e})")
            time.sleep(3)
    
    if retries == 0:
        print("❌ Error crítico: No se pudo conectar a la base de datos después de varios intentos.")
        raise Exception("Database connection failed")

def get_session():
    """
    Generador de sesiones para FastAPI o scripts.
    Usa 'yield' para asegurar que la sesión se cierre después de usarse.
    """
    with Session(engine) as session:
        yield session
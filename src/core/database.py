import os
import time
from sqlalchemy import create_engine, text
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

def bootstrap_system_clients(session: Session):
    """
    Carga los servicios internos 'core' desde variables de entorno.
    Estos son necesarios para que el sistema funcione (Orchestrator <-> Inference).
    NO toca la tabla Client (usuarios/tablets).
    Es idempotente: si ya existen, no hace nada.
    """
    from src.core.models import InferenceClient
    from sqlmodel import select

    # Definir los servicios requeridos
    services = [
        {
            "id": os.getenv("INTERNAL_ORCHESTRATOR_ID"),
            "key": os.getenv("INTERNAL_ORCHESTRATOR_KEY"),
            "role": "admin"
        },
        {
            "id": os.getenv("INTERNAL_INFERENCE_ID"),
            "key": os.getenv("INTERNAL_INFERENCE_KEY"),
            "role": "admin"
        }
    ]

    print("🚀 Verificando servicios internos (Bootstrap)...")
    
    for svc in services:
        if not svc["id"] or not svc["key"]:
            print(f"⚠️  Faltan credenciales para un servicio interno en .env. Saltando...")
            continue

        # Verificar existencia
        statement = select(InferenceClient).where(InferenceClient.client_id == svc["id"])
        existing = session.exec(statement).first()

        if not existing:
            print(f"🛠️  Creando servicio interno: {svc['id']}")
            new_client = InferenceClient(
                client_id=svc["id"],
                api_key=svc["key"],
                role=svc["role"],
                is_active=True
            )
            session.add(new_client)
        else:
            print(f"✅ Servicio interno ya existe: {svc['id']}")
    
    session.commit()

def init_db():
    """
    Inicializa la base de datos: verifica la conexión.
    
    NOTA: Las tablas ya NO se crean automáticamente aquí.
    Usa Alembic para gestionar el esquema:
    - Crear migración: alembic revision --autogenerate -m "descripción"
    - Aplicar migración: alembic upgrade head
    
    Incluye lógica de reintento robusta para esperar a que PostgreSQL esté listo.
    """
    retries = 5
    while retries > 0:
        try:
            print(f"🔄 Intentando conectar a la DB... (Reintentos restantes: {retries})")
            # Importamos los modelos aquí para evitar importaciones circulares
            from src.core import models  # noqa: F401
            
            # Verificar conexión sin crear tablas
            with Session(engine) as session:
                session.exec(text("SELECT 1"))
            
            print("✅ Base de datos conectada exitosamente.")
            
            # Bootstrap de servicios internos
            with Session(engine) as session:
                bootstrap_system_clients(session)
            
            print("ℹ️  Usa 'alembic upgrade head' para aplicar migraciones.")
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
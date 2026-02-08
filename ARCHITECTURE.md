# Cerebro Digital - Arquitectura de la API

## 📁 Estructura del Proyecto

```
src/api/
├── api.py                    # Aplicación principal (38 líneas)
├── utils.py                  # Utilidades compartidas
└── routers/
    ├── __init__.py
    ├── tasks.py              # Router de Tareas
    ├── events.py             # Router de Eventos
    ├── reminders.py          # Router de Recordatorios
    ├── auth.py               # Router de Autenticación (Inference/Client)
    └── chat.py               # Router de Chat (Conversation/Message)
```

## 🎯 Beneficios de la Refactorización

### Antes
- ❌ Un solo archivo de **287 líneas**
- ❌ Lógica duplicada en cada endpoint
- ❌ Difícil de mantener y extender

### Después
- ✅ Archivo principal de **38 líneas**
- ✅ Lógica reutilizable en `utils.py`
- ✅ Routers modulares y organizados
- ✅ Fácil de testear y extender

## 📦 Módulos

### `api.py` - Aplicación Principal
Punto de entrada de la aplicación. Configura FastAPI e incluye los routers.

```python
from src.api.routers import tasks, events, reminders

app = FastAPI(...)
app.include_router(tasks.router)
app.include_router(events.router)
app.include_router(reminders.router)
app.include_router(auth.router)
app.include_router(chat.router)
```

### `routers/auth.py` - Router de Autenticación
Maneja la seguridad para dos tipos de clientes:

1. **Internos (InferenceClient)**: Servicios como el Orquestador que acceden al motor de inferencia.
2. **Externos (Client)**: Aplicaciones de usuario como JotaDesktop.

**Endpoints**:
- `GET /auth/internal` - Valida credenciales de servicio interno (client_id, api_key)
- `GET /auth/client` - Valida clientes de escritorio (client_key)

### `routers/chat.py` - Router de Chat
Gestiona el flujo de conversación, historial y vinculación con sesiones de inferencia.

**Endpoints**:
- `POST /chat/conversation` - Crea una nueva conversación para un cliente
- `GET /chat/history/{conversation_id}` - Obtiene todos los mensajes de una conversación
- `POST /chat/{conversation_id}/messages` - Agrega un mensaje (user/assistant) a la conversación
- `PATCH /chat/session` - Vincula una conversación existente con una `InferenceSession` activa del motor C++

### `utils.py` - Utilidades Compartidas
Funciones reutilizables para optimistic locking y actualización de entidades.

**Funciones principales**:
- `apply_optimistic_locking()` - Verifica versiones y lanza HTTP 409 en conflictos
- `update_entity_fields()` - Actualiza campos de forma segura
- `increment_version()` - Incrementa versión y timestamp

### `routers/tasks.py` - Router de Tareas
Endpoints CRUD para Tasks con filtros por status, priority y event_id.

**Endpoints**:
- `POST /tasks` - Crear tarea
- `GET /tasks` - Listar con filtros
- `GET /tasks/{id}` - Obtener por ID
- `PATCH /tasks/{id}` - Actualizar con optimistic locking
- `DELETE /tasks/{id}` - Eliminar

### `routers/events.py` - Router de Eventos
Endpoints CRUD para Events con filtros por fechas.

**Endpoints**:
- `POST /events` - Crear evento
- `GET /events` - Listar con filtros (start_after, start_before, all_day)
- `GET /events/{id}` - Obtener por ID
- `PATCH /events/{id}` - Actualizar con optimistic locking
- `DELETE /events/{id}` - Eliminar

### `routers/reminders.py` - Router de Recordatorios
Endpoints CRUD para Reminders con filtros avanzados.

**Endpoints**:
- `POST /reminders` - Crear recordatorio
- `GET /reminders` - Listar con filtros (is_completed, task_id, event_id, trigger dates)
- `GET /reminders/{id}` - Obtener por ID
- `PATCH /reminders/{id}` - Actualizar con optimistic locking
- `DELETE /reminders/{id}` - Eliminar

## 🔧 Cómo Extender

### Añadir un nuevo endpoint

1. **Edita el router correspondiente** (ej: `routers/tasks.py`):
```python
@router.get("/tasks/by-priority/{priority}")
def get_tasks_by_priority(priority: int, session: Session = Depends(get_session)):
    tasks = session.exec(select(Task).where(Task.priority == priority)).all()
    return tasks
```

2. **Usa las utilidades compartidas** cuando sea necesario:
```python
from src.api.utils import apply_optimistic_locking, increment_version
```

### Añadir un nuevo router

1. **Crea el archivo** `src/api/routers/nueva_entidad.py`
2. **Define el router**:
```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/nueva-entidad",
    tags=["Nueva Entidad"]
)
```

3. **Incluye en `api.py`**:
```python
from src.api.routers import nueva_entidad
app.include_router(nueva_entidad.router)
```

## 📊 Swagger UI

La documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Los routers están organizados por tags para fácil navegación:
- 🏷️ **Health** - Health check
- 🏷️ **Tasks** - Gestión de tareas
- 🏷️ **Events** - Gestión de eventos
- 🏷️ **Reminders** - Gestión de recordatorios
- 🏷️ **Auth** - Validación de clientes y servicios
- 🏷️ **Chat** - Conversaciones y mensajes

## ✅ Pruebas Realizadas

Todos los endpoints fueron probados exitosamente:

```bash
# Health check
✅ GET /health

# Tasks
✅ POST /tasks
✅ GET /tasks
✅ PATCH /tasks/1 (optimistic locking funciona)

# Events
✅ POST /events
✅ PATCH /events/1 (version 1→2 confirmado)

# Reminders
✅ Todos los endpoints verificados
```

## 🎓 Mejores Prácticas Implementadas

1. **Separación de responsabilidades** - Cada router maneja una entidad
2. **DRY (Don't Repeat Yourself)** - Lógica común en `utils.py`
3. **Documentación automática** - Docstrings en cada endpoint
4. **Type hints** - Tipos explícitos en todas las funciones
5. **Dependency injection** - Uso de `Depends()` para sesiones
6. **HTTP status codes** - Códigos apropiados (201, 204, 404, 409)

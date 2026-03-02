# Chat Endpoints

Estos endpoints gestionan el ciclo de vida de las conversaciones del usuario, el intercambio de mensajes con la IA y la consulta de modelos disponibles.

**URL Base**: `/chat`

## Esquema de Autenticación 🔐

Todos los endpoints bajo `/chat` requieren autenticación. El sistema soporta dos tipos de llamantes ("callers"):

1. **Clientes Directos** (ej. WebApp, CLI):
   - Requiere header: `X-API-Key: <client_key>`
   - Para las rutas de conversaciones, los recursos consultados o creados se asocian automáticamente a este cliente.

2. **Servicios Internos** (ej. Orchestrator, Inference Center):
   - Requieren header principal: `X-API-Key: <service_key>`
   - **IMPORTANTE:** Para operar sobre *conversaciones* y *mensajes*, los servicios deben, además, especificar por cuenta de quién están actuando usando el header secundario obligatoriamente:
     `X-Client-ID: <target_client_id>`
   - Excepción: `/chat/models` es un endpoint global que no opera sobre datos de cliente, por lo que **sólo** requiere el `X-API-Key` y omite el `X-Client-ID`.

---

## `POST /conversations`
Crea una nueva conversación para el cliente objetivo.

**Requisitos de Auth:** 
- `X-API-Key` válido.
- Si quien llama es un Servicio Interno, DEBE incluir `X-Client-ID`.

**Request Body (JSON)**:
- `title` (str, opcional): Título o descripción corta de la conversación.

**Respuesta Exitosa (HTTP 201 Created)**
```json
{
  "id": 1,
  "title": "Ayuda con Python",
  "client_id": "client_abc123",
  "status": "active",
  "created_at": "2026-02-25T10:00:00Z",
  "updated_at": "2026-02-25T10:00:00Z",
  "version": 1
}
```

---

## `GET /conversations`
Lista las conversaciones del cliente, ordenadas desde la más reciente a la más antigua.

**Requisitos de Auth:** 
- `X-API-Key` válido.
- Si quien llama es un Servicio Interno, DEBE incluir `X-Client-ID`.

**Query Parameters**:
- `limit` (int, opcional): Número máximo de conversaciones a devolver (por defecto 50).
- `status_filter` (str, opcional): Filtro por estado (ej. `active`, `archived`).

**Respuesta Exitosa (HTTP 200 OK)**
```json
[
  {
    "id": 1,
    "title": "Ayuda con Python",
    "client_id": "client_abc123",
    "status": "active",
    "created_at": "...",
    "updated_at": "...",
    "version": 1
  }
]
```

---

## `GET /{conversation_id}/messages`
Obtiene los mensajes de una conversación en orden cronológico (del más antiguo al más nuevo).

**Requisitos de Auth:** 
- `X-API-Key` válido.
- Si quien llama es un Servicio Interno, DEBE incluir `X-Client-ID`. (El sistema además verifica que la conversación pertenezca a este cliente).

**Query Parameters**:
- `limit` (int, opcional): Número máximo de mensajes a devolver. Si no se envía, retorna todos.

**Respuesta Exitosa (HTTP 200 OK)**
```json
[
  {
    "id": "msg_xyz789",
    "conversation_id": 1,
    "role": "user",
    "content": "¿Qué es asyncio?",
    "created_at": "2026-02-25T10:01:00Z",
    "updated_at": "2026-02-25T10:01:00Z",
    "version": 1
  }
]
```

---

## `POST /{conversation_id}/messages`
Agrega un nuevo mensaje a una conversación existente.

**Requisitos de Auth:** 
- `X-API-Key` válido.
- Si quien llama es un Servicio Interno, DEBE incluir `X-Client-ID`. (El sistema además verifica que la conversación pertenezca a este cliente).

**Request Body (JSON)**:
- `role` (str, requerido): El rol del emisor. Opciones: `"user"`, `"assistant"`, `"system"`.
- `content` (str, requerido): El contenido en texto del mensaje.

**Respuesta Exitosa (HTTP 201 Created)**
```json
{
  "id": "msg_xyz790",
  "conversation_id": 1,
  "role": "assistant",
  "content": "Asyncio es una librería...",
  "created_at": "2026-02-25T10:01:05Z",
  "updated_at": "2026-02-25T10:01:05Z",
  "version": 1
}
```
*Nota: Este endpoint también actualiza automáticamente el campo `updated_at` de la `Conversation` padre.*

---

## `GET /models`
Devuelve la lista de todos los modelos de IA disponibles con su configuración completa, incluyendo rutas internas.

**Requisitos de Auth:** 
- **Cualquier** `X-API-Key` válido (sea de un Cliente Directo o de un Servicio Interno).
- 🔓 **NO** requiere el header `X-Client-ID`, dado que esta información es global y no dependiente del usuario.

**Respuesta Exitosa (HTTP 200 OK)**
```json
[
  {
    "id": "qwen-7b-chat",
    "name": "Qwen 7b Chat",
    "description": "Modelo auto-descubierto: qwen-7b-chat.gguf",
    "context_window": 2048,
    "file_path": "./models/qwen-7b-chat.gguf",
    "gpu_layers": -1
  }
]
```

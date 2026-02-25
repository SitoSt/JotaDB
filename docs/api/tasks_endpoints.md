# Tasks Endpoints

Gestiona las tareas "To-Do" del usuario. Soporta control de concurrencia mediante *optimistic locking*.

**URL Base**: `/tasks`
**Autenticación Requerida**: Global Bearer Token.

---

## `POST /`
Crea una nueva tarea.

**Request Body (JSON)**:
- `title` (str, requerido): Título descriptivo de la tarea.
- `status` (str, opcional): Estado actual. Opciones típicas: `pending`, `doing`, `done`. Por defecto `pending`.
- `priority` (int, opcional): 1 (Baja) a 5 (Crítica). Por defecto `1`.
- `event_id` (int, opcional): Opcionalmente se puede asociar a un `Event` existente.
- `timing_relative_to_event` (str, opcional): Ej. "before", "during", "after".

**Respuesta Exitosa (HTTP 201 Created)**
```json
{
  "id": 1,
  "title": "Hacer la compra",
  "status": "pending",
  "priority": 3,
  "event_id": null,
  "timing_relative_to_event": null,
  "version": 1,
  "created_at": "...",
  "updated_at": "..."
}
```

---

## `GET /`
Busca y lista tareas aplicando filtros opcionales.

**Query Parameters**:
- `status_filter` (str, opcional): Filtra por estado (ej. `pending`).
- `priority` (int, opcional): Filtra por prioridad exacta.
- `event_id` (int, opcional): Filtra tareas asociadas a un ID de evento.

**Respuesta Exitosa (HTTP 200 OK)**
```json
[
  { "id": 1, "title": "Hacer la compra", "status": "pending", ... }
]
```

---

## `GET /{task_id}`
Obtiene los detalles completos de una tarea específica.

**Respuesta Exitosa (HTTP 200 OK)**
*(Retorna el objeto Task)*

**Errores Posibles**: 
- `404 Not Found`

---

## `PATCH /{task_id}`
Actualiza parcialmente una tarea existente utilizando **optimistic locking**.

**Request Body (JSON)**:
- `version` (int, requerido): La versión actual del registro que conoces.
- *(Cualquier otro campo del modelo que desees actualizar, ej. `status`, `priority`)*

**Comportamiento de Versión**: Si la `version` enviada no coincide con la de la BD, lanzará un error 409. Si coincide, la actualización procede y la versión interna aumenta en 1.

**Errores Posibles**: 
- `409 Conflict`: "Version conflict: expected X, got Y"
- `404 Not Found`

---

## `DELETE /{task_id}`
Elimina una tarea permanentemente.

**Respuesta Exitosa (HTTP 204 No Content)**
*(No devuelve body)*

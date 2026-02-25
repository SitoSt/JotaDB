# Reminders Endpoints

Gestiona los recordatorios y notificaciones del usuario. Pueden existir de forma independiente o asociados a Tareas (`Task`) o Eventos (`Event`). Soportan concurrencia mediante *optimistic locking*.

**URL Base**: `/reminders`
**Autenticación Requerida**: Global Bearer Token.

---

## `POST /`
Crea un nuevo recordatorio.

**Request Body (JSON)**:
- `message` (str, requerido): El mensaje que se le mostrará al usuario.
- `trigger_at` (datetime, requerido): Cuándo debe dispararse el recordatorio (ISO 8601).
- `is_completed` (bool, opcional): Por defecto `false`.
- `task_id` (int, opcional): Asociarlo a una Tarea específica.
- `event_id` (int, opcional): Asociarlo a un Evento específico.

**Respuesta Exitosa (HTTP 201 Created)**
```json
{
  "id": 1,
  "message": "Sacar la basura",
  "trigger_at": "2026-02-25T20:00:00Z",
  "is_completed": false,
  "task_id": null,
  "event_id": null,
  "version": 1,
  "created_at": "...",
  "updated_at": "..."
}
```

---

## `GET /`
Busca y lista recordatorios aplicando filtros avanzados. Útil para sistemas de colas ('pollers') que necesiten saber qué alertar.

**Query Parameters**:
- `is_completed` (bool, opcional): Filtra recordatorios completados o pendientes.
- `task_id` (int, opcional): Filtra por Tarea.
- `event_id` (int, opcional): Filtra por Evento.
- `trigger_after` (datetime, opcional): Recordatorios para después de la fecha.
- `trigger_before` (datetime, opcional): Recordatorios para antes de la fecha.

**Respuesta Exitosa (HTTP 200 OK)**
```json
[
  { "id": 1, "message": "Sacar la basura", "trigger_at": "..." }
]
```

---

## `GET /{reminder_id}`
Obtiene los detalles completos de un recordatorio.

**Respuesta Exitosa (HTTP 200 OK)**
*(Retorna el objeto Reminder)*

**Errores Posibles**: 
- `404 Not Found`

---

## `PATCH /{reminder_id}`
Actualiza parcialmente un recordatorio utilizando **optimistic locking**. Generalmente usado para marcarlo como completado (`is_completed: true`).

**Request Body (JSON)**:
- `version` (int, requerido): La versión actual del registro en tu poder.
- *(Cualquier otro campo, ej. `is_completed` u otro `trigger_at`)*

**Errores Posibles**: 
- `409 Conflict`: Si dos agentes intentan completarlo o editarlo a la vez.
- `404 Not Found`

---

## `DELETE /{reminder_id}`
Elimina un recordatorio permanentemente.

**Respuesta Exitosa (HTTP 204 No Content)**
*(No devuelve body)*

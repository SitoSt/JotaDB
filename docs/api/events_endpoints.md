# Events Endpoints

Gestiona los eventos de calendario del usuario. Soporta control de concurrencia mediante *optimistic locking*.

**URL Base**: `/events`
**Autenticación Requerida**: Ninguna en el código base actual por diseño (aunque a nivel general la API puede estar protegida por middleware en el futuro). Sin embargo, internamente requiere Auth global.

---

## `POST /`
Crea un nuevo evento.

**Request Body (JSON)**:
- `title` (str, requerido): Título del evento.
- `start_at` (datetime, requerido): Fecha y hora de inicio (formato ISO 8601).
- `description` (str, opcional): Detalles sobre el evento.
- `end_at` (datetime, opcional): Fecha y hora de fin.
- `all_day` (bool, opcional): Indica si dura todo el día (por defecto `false`).
- `location` (str, opcional): Ubicación del evento.

**Respuesta Exitosa (HTTP 201 Created)**
```json
{
  "id": 1,
  "title": "Reunión de Equipo",
  "start_at": "2026-02-26T10:00:00Z",
  "end_at": "2026-02-26T11:00:00Z",
  "all_day": false,
  "version": 1,
  "created_at": "...",
  "updated_at": "..."
}
```

---

## `GET /`
Busca y lista eventos aplicando filtros opcionales.

**Query Parameters**:
- `start_after` (datetime, opcional): Retorna eventos que inicien en o después de esta fecha.
- `start_before` (datetime, opcional): Retorna eventos que inicien en o antes de esta fecha.
- `all_day` (bool, opcional): Filtra solo eventos de todo el día o no.

**Respuesta Exitosa (HTTP 200 OK)**
```json
[
  { "id": 1, "title": "Reunión de Equipo", "start_at": "..." }
]
```

---

## `GET /{event_id}`
Obtiene los detalles completos de un evento específico.

**Respuesta Exitosa (HTTP 200 OK)**
*(Retorna el objeto Event)*

**Errores Posibles**: 
- `404 Not Found`

---

## `PATCH /{event_id}`
Actualiza parcialmente un evento existente utilizando **optimistic locking**.

**Request Body (JSON)**:
- `version` (int, requerido): La versión actual del registro que conoces.
- *(Cualquier otro campo del modelo que desees actualizar, ej. `title`, `start_at`)*

**Comportamiento de Versión**: Si la `version` enviada no coincide con la de la base de datos, lanzará un error 409. Si coincide, la actualización procede y la versión interna aumenta en 1.

**Errores Posibles**: 
- `409 Conflict`: "Version conflict: expected X, got Y"
- `404 Not Found`

---

## `DELETE /{event_id}`
Elimina un evento permanentemente.

**Respuesta Exitosa (HTTP 204 No Content)**
*(No devuelve body)*

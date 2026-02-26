# Cambios necesarios en el Backend - Casa Fernando

Este documento describe los cambios que deben aplicarse al backend para que el frontend funcione completamente según los requisitos del usuario.

---

## 1. REGISTRO DE CLIENTES (cedula, direccion, telefono)

**Requisito:** Los clientes se registran con: cédula, nombre, apellido, dirección, teléfono. No permitir cédulas duplicadas.

### Cambios en `app/models/user.py`:
- Añadir columnas: `cedula` (String, unique, nullable para empleados), `direccion`, `telefono`
- Para clientes: cedula obligatoria y única

### Cambios en `app/schemas/auth.py`:
- `UserCreate`: añadir `cedula: str | None = None`, `direccion: str | None = None`, `telefono: str | None = None`
- En `register`: validar que si rol=cliente, cedula es obligatoria
- Validar que no exista otro User o Cliente con la misma cedula al registrar cliente

### Cambios en `app/api/auth.py`:
- En `register`: guardar cedula, direccion, telefono en User cuando se proporcionen
- Validar cedula única: `select(User).where(User.cedula == data.cedula)` o consultar tabla clientes

---

## 2. REGISTRO DE EMPLEADOS (cedula, direccion, telefono, foto)

**Requisito:** Admin crea empleados con: cédula, nombre, apellido, dirección, teléfono, foto.

### Cambios en `app/models/user.py`:
- Añadir: `cedula`, `direccion`, `telefono`, `foto_url` (String, nullable)

### Cambios en `app/schemas/auth.py`:
- `UserCreate` para admin: añadir cedula, direccion, telefono
- Crear `UserCreateAdmin` con campo opcional `foto` (archivo)

### Cambios en `app/api/auth.py`:
- Endpoint `POST /api/auth/register/admin` aceptar FormData para subir foto
- Guardar foto en disco o servicio de almacenamiento, guardar URL en User.foto_url

---

## 3. NOTIFICACIÓN MESONERA - Nombre del cliente y mesonera que atiende

**Requisito:** 
- Cuando el cliente llama, la mesonera debe ver el nombre del cliente que solicita
- Cuando la mesonera acepta "atender", el cliente debe ver el nombre y foto de la mesonera que le atiende

### Cambios en `app/models/notificacion.py`:
- Añadir: `cliente_nombre: str | None`, `cliente_id: int | None`
- Añadir: `mesonera_id: int | None`, `mesonera_nombre: str | None`, `atendida_at: datetime | None`

### Cambios en `app/api/cliente_area.py` - `notificar_mesonera`:
- Aceptar parámetro opcional `cliente_nombre` en query
- Si el cliente está logueado, obtener nombre del token o pasar desde frontend
- Guardar cliente_nombre en NotificacionMesonera

### Cambios en `app/api/mesonera.py` - `marcar_notificacion_atendida`:
- Al marcar atendida: guardar mesonera_id (user.id), mesonera_nombre (user.nombre + apellido)
- Enviar por WebSocket a los clientes conectados un mensaje tipo `mesonera_asignada` con { notif_id, mesa_id, mesonera_nombre, mesonera_foto_url }

### Cambios en WebSocket:
- Crear canal `ws://localhost:8000/api/ws/cliente` donde los clientes en una mesa puedan suscribirse
- Cuando mesonera atiende, broadcast a clientes de esa mesa con datos de la mesonera

---

## 4. LOGIN ADMIN CON USUARIO

**Requisito:** El usuario indicó "usuarios admin con usuario". Actualmente el backend usa email para todos.

**Opción A:** Mantener email para todos (el "usuario" puede ser el email)
**Opción B:** Añadir campo `username` a User y permitir login con username O email para empleados

Si se elige B:
- Añadir `username` a User (unique)
- Modificar login para aceptar `username_or_email` y buscar por cualquiera de los dos

---

## 5. ENDPOINT MESAS DISPONIBLES

**Ya implementado** en `app/api/cliente_area.py`:
- `GET /api/cliente/mesas-disponibles` - Retorna mesas activas sin comanda activa (pendiente, en_preparacion, lista, entregada)

---

## 6. MIGRACIÓN DE BASE DE DATOS

Si se añaden columnas a User o NotificacionMesonera, ejecutar:

```bash
# Si usas Alembic
alembic revision --autogenerate -m "add user cedula direccion telefono foto"
alembic upgrade head
```

O crear script de migración manual para SQLite/PostgreSQL según tu BD.

---

## 7. RESUMEN DE ENDPOINTS NUEVOS/MODIFICADOS

| Endpoint | Cambio |
|----------|--------|
| POST /api/auth/register | Aceptar cedula, direccion, telefono. Validar cedula única |
| POST /api/auth/register/admin | Aceptar cedula, direccion, telefono, foto (multipart) |
| POST /api/cliente/notificar-mesonera | Aceptar cliente_nombre (opcional) |
| POST /api/mesonera/notificaciones/{id}/atender | Guardar mesonera_id, broadcast a cliente |
| GET /api/cliente/mesas-disponibles | **Ya implementado** |

---

## 8. USUARIOS DE PRUEBA

Los usuarios de prueba (admin, mesonera, pos) se crean con `scripts/seed_db.py`. Si se añaden campos a User, actualizar el seed para incluirlos.

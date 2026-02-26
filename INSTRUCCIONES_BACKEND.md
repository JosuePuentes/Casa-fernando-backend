# Instrucciones Backend - Casa Fernando

Documentación del backend para integración con el frontend.

---

## 1. Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login - retorna token JWT y datos del usuario |
| POST | `/api/auth/register` | Registro de clientes (rol `cliente`) |
| POST | `/api/auth/register/admin` | Creación de usuarios del personal (admin, mesonera, punto_venta, cocinero) |
| GET | `/api/auth/me` | Usuario actual (requiere token) |

**Login body:** `{ "email": "string", "password": "string" }`  
**Response:** `{ "access_token": "string", "token_type": "bearer", "user": { "id", "email", "nombre", "apellido", "rol" } }`

---

## 2. Roles y redirección

| Rol | Destino |
|-----|---------|
| `cliente` | Portal de clientes (`/cliente`) |
| `admin` | Panel administrativo |
| `mesonera` | Panel administrativo |
| `punto_venta` | Panel administrativo |
| `cocinero` | Panel administrativo |

---

## 3. Endpoints principales

### Cliente (público o con token)
- `GET /api/cliente/menu` - Menú completo
- `GET /api/cliente/mesas-disponibles` - Mesas sin comanda activa
- `POST /api/cliente/comanda` - Crear comanda (datos cliente + platos)
- `POST /api/cliente/notificar-mesonera?mesa_id=X` - Llamar mesonera

### Mesas (requiere auth mesonera/pos/admin/cocinero)
- `GET /api/mesas` - Listar mesas para selector
- Admin: `GET/POST/PUT/DELETE /api/admin/mesas` - CRUD mesas

### Mesonera (requiere auth)
- `GET /api/mesonera/notificaciones` - Notificaciones pendientes
- `POST /api/mesonera/notificaciones/{id}/atender` - Marcar atendida
- `POST /api/mesonera/comanda` - Crear comanda (mesa_id obligatorio)
- `GET /api/mesonera/comandas` - Listar comandas

### Punto de venta
- `POST /api/pos/comanda` - Crear comanda

### Facturación
- `GET /api/facturacion/comandas?nombre=&cedula=&fecha_desde=&fecha_hasta=` - Buscar
- `GET /api/facturacion/comandas/{id}` - Detalle
- `PATCH /api/comandas/{id}` - Actualizar estado/forma de pago

---

## 4. WebSocket

- **URL:** `ws://host/api/ws/mesonera`
- Al recibir: `{ "type": "notificacion_cliente", "vibrar": true, "mesa_id", "mensaje", "id" }` → usar `navigator.vibrate([200, 100, 200])`

---

## 5. CORS

Configurar en variables de entorno:
- **Desarrollo:** `CORS_ORIGINS=http://localhost:3000`
- **Producción:** `CORS_ORIGINS=http://localhost:3000,https://tu-app.vercel.app`

Separar múltiples orígenes por coma.

---

## 6. Usuarios de prueba (seed_db.py)

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@casafernando.com | admin123 |
| Mesonera | mesonera@casafernando.com | mesonera123 |
| POS | pos@casafernando.com | pos123 |
| Cocinero | cocinero@casafernando.com | cocinero123 |

# Instrucciones para el Frontend - Casa Fernando

Backend API: `http://localhost:8000` (o la URL donde corra el servidor)

Documentación Swagger: `http://localhost:8000/docs`

---

## 1. AUTENTICACIÓN

### Login
- **POST** `/api/auth/login`
- Body: `{ "email": "string", "password": "string" }`
- Response: `{ "access_token": "string", "token_type": "bearer", "user": { "id", "email", "nombre", "apellido", "rol" } }`
- Guardar el token para enviarlo en header: `Authorization: Bearer <token>`

### Registro (clientes)
- **POST** `/api/auth/register`
- Body: `{ "email", "password", "nombre", "apellido", "rol": "cliente" }`

### Usuario actual
- **GET** `/api/auth/me` (requiere token)

### Roles
- `admin` - Administrador
- `mesonera` - Mesonera
- `punto_venta` - Punto de venta
- `cliente` - Cliente

---

## 2. ÁREA CLIENTE (puede ser público o con login)

### Ver menú
- **GET** `/api/cliente/menu`
- Response: `[{ "id", "nombre", "descripcion", "precio", "imagen_url", "categoria" }]`

### Crear comanda (desde área cliente)
- **POST** `/api/cliente/comanda`
- Body:
```json
{
  "cliente": {
    "cedula": "string",
    "nombre": "string",
    "apellido": "string",
    "direccion": "string (opcional)",
    "telefono": "string",
    "email": "string (opcional)"
  },
  "mesa_id": null,
  "platos": [
    { "plato_id": 1, "cantidad": 2, "observaciones": "string (opcional)" }
  ],
  "forma_pago": "efectivo|tarjeta|transferencia|otro (opcional)",
  "origen": "area_cliente",
  "observaciones": "string (opcional)"
}
```
- `mesa_id` es opcional para área cliente (si el cliente está en una mesa puede enviarlo)

### Notificar mesonera (botón mantener presionado)
- **POST** `/api/cliente/notificar-mesonera?mesa_id=1`
- Parámetros query: `mesa_id` (opcional), `mensaje` (opcional, default: "El cliente solicita atención")
- Al enviar, las mesoneras conectadas por WebSocket reciben la notificación y deben vibrar el dispositivo

---

## 3. MÓDULO MESONERA (requiere token mesonera/admin/pos)

### Listar mesas (para elegir al crear comanda)
- **GET** `/api/mesas`
- Response: `[{ "id", "numero", "capacidad", "ubicacion" }]`

### Crear comanda
- **POST** `/api/mesonera/comanda`
- Body igual que área cliente pero **`mesa_id` es OBLIGATORIO** y `origen`: `"mesonera"`
- Requiere datos del cliente (cedula, nombre, apellido, dirección, teléfono)

### Listar comandas
- **GET** `/api/mesonera/comandas?estado=pendiente` (estado opcional)

### Notificaciones pendientes
- **GET** `/api/mesonera/notificaciones`
- Response: `[{ "id", "mesa_id", "mensaje", "created_at" }]`

### Marcar notificación atendida
- **POST** `/api/mesonera/notificaciones/{id}/atender`

### WebSocket para recibir notificaciones en tiempo real
- **WS** `ws://localhost:8000/api/ws/mesonera`
- Al conectarse, recibe mensajes cuando un cliente llama. Formato: `{ "type": "notificacion_cliente", "vibrar": true, "mesa_id", "mensaje", "id" }`
- Usar `navigator.vibrate([200, 100, 200])` al recibir para vibrar el teléfono

---

## 4. PUNTO DE VENTA (requiere token pos/admin/mesonera)

### Listar mesas
- **GET** `/api/mesas`

### Crear comanda
- **POST** `/api/pos/comanda`
- Body igual pero `origen`: `"punto_venta"` y **`mesa_id` OBLIGATORIO**

---

## 5. FACTURACIÓN (requiere token mesonera/pos/admin)

### Buscar comandas
- **GET** `/api/facturacion/comandas`
- Query params:
  - `nombre` - Buscar por nombre o apellido del cliente
  - `cedula` - Buscar por cédula
  - `fecha_desde` - YYYY-MM-DD
  - `fecha_hasta` - YYYY-MM-DD
- Response: `[{ "id", "numero", "mesa_numero", "cliente_nombre", "cliente_apellido", "cliente_cedula", "cliente_telefono", "total", "estado", "forma_pago", "created_at" }]`

### Detalle de comanda
- **GET** `/api/facturacion/comandas/{id}`
- Response: objeto con cliente, mesa, subtotal, impuesto, total, detalles (platos, cantidades, precios)

### Actualizar estado comanda
- **PATCH** `/api/comandas/{id}`
- Body: `{ "estado": "pendiente|en_preparacion|lista|entregada|pagada|cancelada", "forma_pago": "efectivo|tarjeta|..." }`

---

## 6. ADMINISTRACIÓN (requiere token admin)

### Categorías
- **GET** `/api/admin/categorias`
- **POST** `/api/admin/categorias` - Body: `{ "nombre", "descripcion", "orden" }`

### Platos
- **GET** `/api/admin/platos`
- **POST** `/api/admin/platos` - Body: `{ "nombre", "descripcion", "precio", "categoria_id", "imagen_url", "disponible" }`
- **PUT** `/api/admin/platos/{id}` - Body parcial
- **DELETE** `/api/admin/platos/{id}`

### Mesas
- **GET** `/api/admin/mesas`
- **POST** `/api/admin/mesas` - Body: `{ "numero", "capacidad", "ubicacion" }`
- **PUT** `/api/admin/mesas/{id}` - Body: `{ "numero", "capacidad", "ubicacion", "activa" }`
- **DELETE** `/api/admin/mesas/{id}` - Desactiva la mesa

### Usuarios (empleados)
- **POST** `/api/auth/register/admin` - Body: `{ "email", "password", "nombre", "apellido", "rol": "admin|mesonera|punto_venta" }`

---

## 7. ENUMERACIONES

### FormaPago
`efectivo`, `tarjeta`, `transferencia`, `otro`

### EstadoComanda
`pendiente`, `en_preparacion`, `lista`, `entregada`, `pagada`, `cancelada`

### OrigenComanda
`area_cliente`, `mesonera`, `punto_venta`

---

## 8. USUARIOS DE PRUEBA (después de ejecutar seed_db.py)

| Rol     | Email                      | Contraseña  |
|---------|----------------------------|-------------|
| Admin   | admin@casafernando.com     | admin123    |
| Mesonera| mesonera@casafernando.com  | mesonera123 |
| POS     | pos@casafernando.com       | pos123      |

---

## 9. ESTRUCTURA SUGERIDA DEL FRONTEND

```
frontend/
├── src/
│   ├── pages/
│   │   ├── cliente/          # Área cliente: menú, comanda, botón llamar mesonera
│   │   ├── mesonera/         # Módulo mesonera: comandas, notificaciones, WebSocket
│   │   ├── pos/              # Punto de venta: comandas
│   │   ├── facturacion/      # Búsqueda, filtros, detalle comandas
│   │   └── admin/            # CRUD platos, categorías, mesas, usuarios
│   ├── services/             # Llamadas API (axios/fetch)
│   ├── hooks/                # useAuth, useWebSocket
│   ├── components/           # Componentes reutilizables
│   └── context/              # AuthContext, etc.
```

---

## 10. CORS

El backend tiene CORS habilitado para todos los orígenes (`*`). En producción configurar orígenes específicos.

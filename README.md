# Casa Fernando - Backend Restaurante

Backend en Python (FastAPI) para sistema ERP de restaurante. Incluye área de cliente, módulo mesonera, punto de venta y facturación.

## Características

- **Área Cliente**: Ver menú, hacer comandas, botón para notificar mesonera (vibración en tiempo real)
- **Módulo Mesonera**: Recibir notificaciones, crear comandas con platos y forma de pago
- **Punto de Venta**: Crear comandas
- **Facturación**: Buscar por nombre, cédula, filtrar por fecha
- **Administración**: CRUD de platos, categorías, mesas, usuarios

## Requisitos

- Python 3.11+
- pip

## Instalación

```bash
cd "Casa Fernando Backend"
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Configuración

Copiar `.env.example` a `.env` y ajustar variables si es necesario.

## Ejecutar

```bash
# Cargar datos iniciales (admin, mesonera, platos, mesas)
python scripts/seed_db.py

# Iniciar servidor
python run.py
```

API disponible en: http://localhost:8000  
Documentación Swagger: http://localhost:8000/docs

## Usuarios iniciales (después de seed)

| Rol    | Email                     | Contraseña   |
|--------|---------------------------|--------------|
| Admin  | admin@casafernando.com    | admin123     |
| Mesonera | mesonera@casafernando.com | mesonera123 |
| POS    | pos@casafernando.com      | pos123       |

## Endpoints principales

### Área Cliente (público)
- `GET /api/cliente/menu` - Menú completo
- `POST /api/cliente/comanda` - Crear comanda (requiere datos: cédula, nombre, apellido, dirección, teléfono)
- `POST /api/cliente/notificar-mesonera?mesa_id=1` - Notificar mesonera (vibra en dispositivos conectados)

### Mesas (requiere auth mesonera/POS)
- `GET /api/mesas` - Listar mesas para elegir al crear comanda

### Mesonera (requiere auth)
- `GET /api/mesonera/notificaciones` - Notificaciones pendientes
- `POST /api/mesonera/comanda` - Crear comanda (mesa_id obligatorio)
- `GET /api/mesonera/comandas` - Listar comandas

### Punto de Venta (requiere auth)
- `POST /api/pos/comanda` - Crear comanda (mesa_id obligatorio)

### Facturación (requiere auth)
- `GET /api/facturacion/comandas?nombre=...&cedula=...&fecha_desde=...&fecha_hasta=...` - Buscar comandas
- `GET /api/facturacion/comandas/{id}` - Detalle comanda

### WebSocket
- `WS /api/ws/mesonera` - Conexión para recibir notificaciones en tiempo real (vibración)

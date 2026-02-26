# Desplegar Casa Fernando Backend en Render

## Variables de entorno para Render

| NAME | VALUE |
|------|-------|
| `SECRET_KEY` | `casa-fernando-clave-secreta-produccion-2024` |
| `MONGODB_URL` | `mongodb+srv://casafernando1:TU_PASSWORD@cluster0.3u0u9w0.mongodb.net/casa_fernando?retryWrites=true&w=majority` |

## Configuración del formulario

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Importante

- El archivo `runtime.txt` fija Python 3.12 para evitar errores de build con pydantic.
- La base de datos es **MongoDB** (no SQLite).
- En MongoDB Atlas, permite el acceso desde cualquier IP (0.0.0.0/0) para que Render pueda conectarse.

"""Configuración de base de datos MongoDB."""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import get_settings

settings = get_settings()
client: AsyncIOMotorClient | None = None


async def init_db():
    """Inicializar conexión MongoDB y documentos Beanie."""
    global client
    from app.models.user import User
    from app.models.cliente import Cliente
    from app.models.plato import Plato, CategoriaPlato
    from app.models.comanda import Comanda
    from app.models.mesa import Mesa
    from app.models.notificacion import NotificacionMesonera

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client.get_default_database()
    await init_beanie(
        database=database,
        document_models=[User, Cliente, CategoriaPlato, Plato, Mesa, Comanda, NotificacionMesonera],
    )

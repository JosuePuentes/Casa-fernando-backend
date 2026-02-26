"""Configuración de base de datos."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base para todos los modelos."""
    pass


async def get_db():
    """Dependencia para obtener sesión de base de datos."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Inicializar tablas de la base de datos."""
    from app.models import User, Cliente, Plato, CategoriaPlato, Comanda, ComandaDetalle, Mesa, NotificacionMesonera
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

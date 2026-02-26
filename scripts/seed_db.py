"""Script para cargar datos iniciales en MongoDB."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db
from app.models.user import User
from app.models.plato import Plato, CategoriaPlato
from app.models.mesa import Mesa
from app.core.security import get_password_hash
from app.models.user import RolUsuario


async def seed():
    await init_db()

    if not await User.find_one(User.email == "admin@casafernando.com"):
        admin = User(
            email="admin@casafernando.com",
            hashed_password=get_password_hash("admin123"),
            nombre="Administrador",
            apellido="Sistema",
            rol=RolUsuario.ADMIN,
        )
        await admin.insert()
        print("Admin creado: admin@casafernando.com / admin123")

    if not await User.find_one(User.email == "mesonera@casafernando.com"):
        mesonera = User(
            email="mesonera@casafernando.com",
            hashed_password=get_password_hash("mesonera123"),
            nombre="María",
            apellido="Mesonera",
            rol=RolUsuario.MESONERA,
        )
        await mesonera.insert()
        print("Mesonera creada: mesonera@casafernando.com / mesonera123")

    if not await User.find_one(User.email == "pos@casafernando.com"):
        pos_user = User(
            email="pos@casafernando.com",
            hashed_password=get_password_hash("pos123"),
            nombre="Carlos",
            apellido="Caja",
            rol=RolUsuario.PUNTO_VENTA,
        )
        await pos_user.insert()
        print("POS creado: pos@casafernando.com / pos123")

    categorias_data = [
        ("Entradas", "Entradas y aperitivos", 1),
        ("Platos Fuertes", "Platos principales", 2),
        ("Bebidas", "Bebidas y refrescos", 3),
        ("Postres", "Postres y dulces", 4),
    ]
    cat_ids = {}
    for nombre, desc, orden in categorias_data:
        c = await CategoriaPlato.find_one(CategoriaPlato.nombre == nombre)
        if not c:
            c = CategoriaPlato(nombre=nombre, descripcion=desc, orden=orden)
            await c.insert()
            print(f"Categoría creada: {nombre}")
        cat_ids[nombre] = str(c.id)

    platos_data = [
        ("Ensalada César", "Ensalada con pollo y aderezo césar", 8.50, "Entradas"),
        ("Sopa del día", "Sopa casera del día", 5.00, "Entradas"),
        ("Arroz con pollo", "Arroz con pollo y vegetales", 12.00, "Platos Fuertes"),
        ("Pescado frito", "Pescado fresco con patacones", 15.00, "Platos Fuertes"),
        ("Hamburguesa", "Hamburguesa con papas fritas", 10.00, "Platos Fuertes"),
        ("Limonada", "Limonada natural", 3.00, "Bebidas"),
        ("Café", "Café americano o con leche", 2.50, "Bebidas"),
        ("Agua mineral", "Agua mineral con o sin gas", 2.00, "Bebidas"),
        ("Flan", "Flan de vainilla", 4.50, "Postres"),
        ("Brownie", "Brownie con helado", 5.00, "Postres"),
    ]
    for nombre, desc, precio, cat in platos_data:
        if not await Plato.find_one(Plato.nombre == nombre) and cat in cat_ids:
            p = Plato(categoria_id=cat_ids[cat], nombre=nombre, descripcion=desc, precio=precio)
            await p.insert()
            print(f"Plato creado: {nombre}")

    for i in range(1, 11):
        if not await Mesa.find_one(Mesa.numero == str(i)):
            m = Mesa(numero=str(i), capacidad=4)
            await m.insert()
            print(f"Mesa creada: {i}")

    print("\nSeed completado.")


if __name__ == "__main__":
    asyncio.run(seed())

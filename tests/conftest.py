import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_galpyra.db")
os.environ.setdefault("ENVIRONMENT", "test")

from app.core.dependencies import get_db  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.alimentacion.models import AlimentacionRegistro  # noqa: E402
from app.modules.auth.models import RefreshToken, Usuario  # noqa: E402
from app.modules.aves.models import LoteAve, MovimientoAve  # noqa: E402
from app.modules.galpones.models import Galpon  # noqa: E402
from app.modules.inventario_foto.models import InventarioFotoJob  # noqa: E402
from app.modules.produccion.models import ProduccionHuevo  # noqa: E402
from app.modules.reportes.models import ReporteGenerado  # noqa: E402
from app.modules.sanidad.models import EventoSanitario  # noqa: E402
from app.modules.sync.models import SyncLog  # noqa: E402
from app.shared.base_model import Base  # noqa: E402
from app.shared.enums import EstadoGalpon, EstadoLote, RolUsuario  # noqa: E402

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_galpyra.db"
test_engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    async with TestSessionLocal() as session:
        for model in [
            InventarioFotoJob,
            SyncLog,
            ReporteGenerado,
            AlimentacionRegistro,
            EventoSanitario,
            ProduccionHuevo,
            MovimientoAve,
            LoteAve,
            Galpon,
            RefreshToken,
            Usuario,
        ]:
            await session.execute(delete(model))
        await session.commit()

    yield


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def seeded_admin():
    async with TestSessionLocal() as session:
        admin = Usuario(
            nombre="Administrador GALPyra",
            email="admin@galpyra.com",
            password_hash=hash_password("Admin123*"),
            rol=RolUsuario.ADMIN,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return admin


@pytest_asyncio.fixture
async def seeded_galpon_lote(seeded_admin):
    async with TestSessionLocal() as session:
        galpon = Galpon(
            nombre="Galpon Test",
            ubicacion="Santander",
            capacidad=500,
            estado=EstadoGalpon.ACTIVO,
            descripcion="Galpon de pruebas",
            propietario_id=seeded_admin.id,
        )
        session.add(galpon)
        await session.flush()

        lote = LoteAve(
            codigo_lote=f"L-TEST-{uuid4().hex[:6]}",
            tipo_ave="PONEDORA",
            raza="Hy-Line",
            cantidad_inicial=300,
            cantidad_actual=300,
            fecha_ingreso=datetime.now(timezone.utc),
            galpon_id=galpon.id,
            estado=EstadoLote.ACTIVO,
        )
        session.add(lote)
        await session.commit()
        await session.refresh(galpon)
        await session.refresh(lote)

        return {"galpon": galpon, "lote": lote}

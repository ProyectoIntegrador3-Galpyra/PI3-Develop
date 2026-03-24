from datetime import datetime, timezone

import pytest

from app.modules.aves.models import MovimientoAve
from app.modules.produccion.models import ProduccionHuevo
from app.shared.enums import TipoMovimientoAve
from tests.conftest import TestSessionLocal


@pytest.mark.asyncio
async def test_dashboard_vacio(client, auth_headers):
    response = await client.get("/api/dashboard", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "total_aves_activas" in data
    assert "produccion_ultimos_7_dias" in data
    assert "tasa_mortalidad_porcentaje" in data
    assert "alertas" in data
    assert data["total_aves_activas"] == 0
    assert data["produccion_ultimos_7_dias"] == 0
    assert data["tasa_mortalidad_porcentaje"] == 0.0
    assert data["alertas"] == []


@pytest.mark.asyncio
async def test_dashboard_con_datos(client, seeded_galpon_lote, auth_headers):
    galpon = seeded_galpon_lote["galpon"]
    lote = seeded_galpon_lote["lote"]

    async with TestSessionLocal() as session:
        produccion = ProduccionHuevo(
            galpon_id=galpon.id,
            lote_id=lote.id,
            fecha=datetime.now(timezone.utc),
            cantidad=250,
            huevos_rotos=5,
        )
        session.add(produccion)

        mortalidad = MovimientoAve(
            lote_id=lote.id,
            tipo_movimiento=TipoMovimientoAve.MORTALIDAD,
            cantidad=10,
            causa="Enfermedad",
            fecha=datetime.now(timezone.utc),
        )
        session.add(mortalidad)
        await session.commit()

    response = await client.get("/api/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["total_aves_activas"] == 300
    assert data["produccion_ultimos_7_dias"] == 250
    # tasa: 10 bajas / 300 iniciales * 100 = 3.33
    assert data["tasa_mortalidad_porcentaje"] == round(10 / 300 * 100, 2)
    assert data["alertas"] == []

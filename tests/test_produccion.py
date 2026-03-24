from datetime import datetime, timezone

import pytest


@pytest.mark.asyncio
async def test_porcentaje_postura_automatico(client, seeded_galpon_lote, auth_headers):
    galpon = seeded_galpon_lote["galpon"]
    lote = seeded_galpon_lote["lote"]

    payload = {
        "galpon_id": galpon.id,
        "lote_id": lote.id,
        "fecha": datetime.now(timezone.utc).isoformat(),
        "cantidad": 120,
        "huevos_rotos": 2,
        "observaciones": "Produccion diaria",
    }

    response = await client.post("/api/produccion", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["porcentaje_postura"] == round(120 / 300 * 100, 2)


@pytest.mark.asyncio
async def test_fecha_unica_por_lote(client, seeded_galpon_lote, auth_headers):
    galpon = seeded_galpon_lote["galpon"]
    lote = seeded_galpon_lote["lote"]
    fecha = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)

    payload = {
        "galpon_id": galpon.id,
        "lote_id": lote.id,
        "fecha": fecha.isoformat(),
        "cantidad": 140,
    }

    first = await client.post("/api/produccion", json=payload, headers=auth_headers)
    assert first.status_code == 200

    second_payload = {
        "galpon_id": galpon.id,
        "lote_id": lote.id,
        "fecha": fecha.replace(hour=12).isoformat(),
        "cantidad": 150,
    }
    second = await client.post("/api/produccion", json=second_payload, headers=auth_headers)
    assert second.status_code == 409

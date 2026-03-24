from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.asyncio
async def test_historial_mortalidad_con_filtros(client, seeded_galpon_lote, auth_headers):
    lote = seeded_galpon_lote["lote"]

    fecha_1 = datetime.now(timezone.utc) - timedelta(days=4)
    fecha_2 = datetime.now(timezone.utc) - timedelta(days=1)

    for fecha, cantidad in [(fecha_1, 5), (fecha_2, 10)]:
        response = await client.post(
            "/api/mortalidad",
            json={
                "lote_id": lote.id,
                "cantidad": cantidad,
                "causa": "Prueba",
                "fecha": fecha.isoformat(),
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    inicio = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    fin = datetime.now(timezone.utc).isoformat()

    historial = await client.get(
        f"/api/lotes/{lote.id}/mortalidad",
        params={"fecha_inicio": inicio, "fecha_fin": fin},
        headers=auth_headers,
    )
    assert historial.status_code == 200

    data = historial.json()["data"]
    assert data["total_mortalidad"] == 10
    assert data["tasa_mortalidad_porcentaje"] == round(10 / 300 * 100, 2)
    assert len(data["registros"]) == 1

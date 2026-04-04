import pytest


@pytest.mark.asyncio
async def test_inventario_procesar_acepta_campo_imagen(
    client,
    seeded_galpon_lote,
    auth_headers,
):
    lote = seeded_galpon_lote["lote"]

    response = await client.post(
        "/api/inventario/procesar",
        data={"lote_id": lote.id},
        files={"imagen": ("inventario.jpg", b"fake-image-bytes", "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["job_id"]

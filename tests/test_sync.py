from datetime import datetime, timezone
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_sync_batch(client, seeded_galpon_lote):
    galpon = seeded_galpon_lote["galpon"]
    lote = seeded_galpon_lote["lote"]

    operacion_produccion_id = str(uuid4())
    operacion_mov_id = str(uuid4())

    payload = {
        "operaciones": [
            {
                "id": str(uuid4()),
                "operacion": "UPSERT",
                "entidad": "produccion_huevos",
                "payload": {
                    "id": operacion_produccion_id,
                    "galpon_id": galpon.id,
                    "lote_id": lote.id,
                    "fecha": datetime.now(timezone.utc).isoformat(),
                    "cantidad": 320,
                    "huevos_rotos": 4,
                    "observaciones": "Sync app movil",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": str(uuid4()),
                "operacion": "UPSERT",
                "entidad": "movimiento_aves",
                "payload": {
                    "id": operacion_mov_id,
                    "lote_id": lote.id,
                    "tipo_movimiento": "MORTALIDAD",
                    "cantidad": 3,
                    "causa": "Prueba sync",
                    "fecha": datetime.now(timezone.utc).isoformat(),
                    "observaciones": "test",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
    }

    response = await client.post("/api/sync", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["procesadas"] == 2
    assert body["data"]["fallidas"] == 0

    logs_response = await client.get("/api/sync/logs")
    assert logs_response.status_code == 200
    logs_body = logs_response.json()
    assert logs_body["success"] is True
    assert len(logs_body["data"]) == 2


@pytest.mark.asyncio
async def test_inventario_foto_basico(client, seeded_galpon_lote):
    lote = seeded_galpon_lote["lote"]

    process_response = await client.post(
        "/api/inventario/procesar",
        data={"lote_id": lote.id},
        files={"file": ("inventario.jpg", b"fake-image-bytes", "image/jpeg")},
    )
    assert process_response.status_code == 200
    process_body = process_response.json()
    assert process_body["success"] is True
    job_id = process_body["data"]["job_id"]

    confirm_response = await client.post(
        "/api/inventario/confirmar",
        json={
            "job_id": job_id,
            "conteo_confirmado": 123,
            "lote_id": lote.id,
        },
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["success"] is True

    get_response = await client.get(f"/api/inventario/jobs/{job_id}")
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["data"]["conteo_confirmado"] == 123

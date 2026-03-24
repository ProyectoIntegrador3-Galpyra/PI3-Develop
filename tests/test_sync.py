from datetime import datetime, timezone
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_sync_batch(client, seeded_galpon_lote, auth_headers):
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

    response = await client.post("/api/sync", json=payload, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["procesadas"] == 2
    assert body["data"]["fallidas"] == 0

    logs_response = await client.get("/api/sync/logs", headers=auth_headers)
    assert logs_response.status_code == 200
    logs_body = logs_response.json()
    assert logs_body["success"] is True
    assert len(logs_body["data"]) == 2


@pytest.mark.asyncio
async def test_inventario_foto_basico(client, seeded_galpon_lote, auth_headers):
    lote = seeded_galpon_lote["lote"]

    process_response = await client.post(
        "/api/inventario/procesar",
        data={"lote_id": lote.id},
        files={"file": ("inventario.jpg", b"fake-image-bytes", "image/jpeg")},
        headers=auth_headers,
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
        headers=auth_headers,
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["success"] is True

    get_response = await client.get(f"/api/inventario/jobs/{job_id}", headers=auth_headers)
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["data"]["conteo_confirmado"] == 123


@pytest.mark.asyncio
async def test_sync_entidades_faltantes_y_delete(client, seeded_galpon_lote, auth_headers):
    admin = seeded_galpon_lote["admin"]
    galpon = seeded_galpon_lote["galpon"]
    lote = seeded_galpon_lote["lote"]

    now_iso = datetime.now(timezone.utc).isoformat()
    nuevo_galpon_id = str(uuid4())
    nuevo_lote_id = str(uuid4())
    nuevo_evento_id = str(uuid4())
    nueva_alimentacion_id = str(uuid4())

    payload = {
        "operaciones": [
            {
                "id": str(uuid4()),
                "operacion": "CREATE",
                "entidad": "galpones",
                "payload": {
                    "id": nuevo_galpon_id,
                    "nombre": "Galpon Sync",
                    "ubicacion": "Zona 2",
                    "capacidad": 700,
                    "estado": "ACTIVO",
                    "propietario_id": admin.id,
                    "updated_at": now_iso,
                },
                "created_at": now_iso,
            },
            {
                "id": str(uuid4()),
                "operacion": "CREATE",
                "entidad": "lotes_aves",
                "payload": {
                    "id": nuevo_lote_id,
                    "codigo_lote": "SYNC-LOTE-001",
                    "tipo_ave": "PONEDORA",
                    "raza": "Hy-Line",
                    "cantidad_inicial": 150,
                    "cantidad_actual": 150,
                    "fecha_ingreso": now_iso,
                    "galpon_id": nuevo_galpon_id,
                    "estado": "ACTIVO",
                    "updated_at": now_iso,
                },
                "created_at": now_iso,
            },
            {
                "id": str(uuid4()),
                "operacion": "CREATE",
                "entidad": "eventos_sanitarios",
                "payload": {
                    "id": nuevo_evento_id,
                    "lote_id": lote.id,
                    "galpon_id": galpon.id,
                    "tipo_evento": "DIAGNOSTICO",
                    "descripcion": "Evento sync",
                    "producto": "Suplemento",
                    "dosis": "10ml",
                    "responsable": "Tecnico",
                    "fecha": now_iso,
                    "updated_at": now_iso,
                },
                "created_at": now_iso,
            },
            {
                "id": str(uuid4()),
                "operacion": "CREATE",
                "entidad": "alimentacion_registros",
                "payload": {
                    "id": nueva_alimentacion_id,
                    "galpon_id": galpon.id,
                    "lote_id": lote.id,
                    "fecha": now_iso,
                    "tipo_alimento": "Concentrado",
                    "cantidad_kg": 100.5,
                    "costo": 220000,
                    "updated_at": now_iso,
                },
                "created_at": now_iso,
            },
            {
                "id": str(uuid4()),
                "operacion": "DELETE",
                "entidad": "alimentacion_registros",
                "payload": {
                    "id": nueva_alimentacion_id,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
    }

    response = await client.post("/api/sync", json=payload, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["procesadas"] == 5
    assert body["data"]["fallidas"] == 0

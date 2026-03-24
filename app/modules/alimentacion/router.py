# CORRECCIÓN APLICADA: [1 — Autenticación en endpoints]
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.modules.auth.models import Usuario
from app.modules.alimentacion.schemas import AlimentacionCreate, AlimentacionUpdate
from app.modules.alimentacion.service import AlimentacionService

router = APIRouter(prefix="/alimentacion", tags=["Alimentacion"])


@router.get("")
async def list_alimentacion(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await AlimentacionService.list(db)
    return success_response(
        message="Registros de alimentacion obtenidos",
        data=[item.model_dump() for item in data],
    )


@router.get("/rango")
async def list_alimentacion_rango(
    fecha_inicio: datetime = Query(...),
    fecha_fin: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await AlimentacionService.list_rango(db, fecha_inicio, fecha_fin)
    return success_response(
        message="Registros de alimentacion por rango obtenidos",
        data=[item.model_dump() for item in data],
    )


@router.get("/conversion/{lote_id}")
async def get_conversion_alimenticia(
    lote_id: str,
    fecha_inicio: datetime | None = Query(default=None),
    fecha_fin: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await AlimentacionService.calcular_conversion_alimenticia(
        db,
        lote_id=lote_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    return success_response(
        message="Conversion alimenticia obtenida",
        data=data.model_dump(),
    )


@router.get("/{registro_id}")
async def get_alimentacion(
    registro_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await AlimentacionService.get_by_id(db, registro_id)
    return success_response(message="Registro de alimentacion obtenido", data=data.model_dump())


@router.post("")
async def create_alimentacion(
    payload: AlimentacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await AlimentacionService.create(db, payload)
    return success_response(message="Registro de alimentacion creado", data=data.model_dump())


@router.put("/{registro_id}")
async def update_alimentacion(
    registro_id: str,
    payload: AlimentacionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await AlimentacionService.update(db, registro_id, payload)
    return success_response(message="Registro de alimentacion actualizado", data=data.model_dump())


@router.delete("/{registro_id}")
async def delete_alimentacion(
    registro_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    await AlimentacionService.delete(db, registro_id)
    return success_response(message="Registro de alimentacion eliminado", data=None)

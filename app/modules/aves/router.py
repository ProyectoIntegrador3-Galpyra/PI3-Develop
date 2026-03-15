from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.responses import success_response
from app.modules.aves.schemas import (
    LoteAveCreate,
    LoteAveUpdate,
    MovimientoIngresoCreate,
    MovimientoMortalidadCreate,
)
from app.modules.aves.service import AvesService
from app.shared.enums import TipoMovimientoAve

router = APIRouter(tags=["Aves"])


@router.get("/lotes")
async def list_lotes(db: AsyncSession = Depends(get_db)) -> dict:
    # Seguridad desactivada en modo desarrollo abierto.
    data = await AvesService.list_lotes(db)
    return success_response(message="Lotes obtenidos", data=[item.model_dump() for item in data])


@router.get("/lotes/galpon/{galpon_id}")
async def list_lotes_por_galpon(galpon_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    data = await AvesService.list_lotes_por_galpon(db, galpon_id)
    return success_response(
        message="Lotes por galpon obtenidos",
        data=[item.model_dump() for item in data],
    )


@router.get("/lotes/{lote_id}")
async def get_lote(lote_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    data = await AvesService.get_lote(db, lote_id)
    return success_response(message="Lote obtenido", data=data.model_dump())


@router.post("/lotes")
async def create_lote(payload: LoteAveCreate, db: AsyncSession = Depends(get_db)) -> dict:
    data = await AvesService.create_lote(db, payload)
    return success_response(message="Lote creado", data=data.model_dump())


@router.put("/lotes/{lote_id}")
async def update_lote(
    lote_id: str,
    payload: LoteAveUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    data = await AvesService.update_lote(db, lote_id, payload)
    return success_response(message="Lote actualizado", data=data.model_dump())


@router.delete("/lotes/{lote_id}")
async def delete_lote(lote_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    await AvesService.delete_lote(db, lote_id)
    return success_response(message="Lote eliminado", data=None)


@router.post("/ingresos")
async def registrar_ingreso(
    payload: MovimientoIngresoCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    data = await AvesService.registrar_movimiento(
        db,
        payload=payload,
        tipo_forzado=TipoMovimientoAve.INGRESO,
    )
    return success_response(message="Ingreso registrado", data=data.model_dump())


@router.post("/mortalidad")
async def registrar_mortalidad(
    payload: MovimientoMortalidadCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    data = await AvesService.registrar_movimiento(
        db,
        payload=payload,
        tipo_forzado=TipoMovimientoAve.MORTALIDAD,
    )
    return success_response(message="Mortalidad registrada", data=data.model_dump())

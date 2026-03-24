# CORRECCIÓN APLICADA: [1 — Autenticación en endpoints]
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.modules.auth.models import Usuario
from app.modules.sanidad.schemas import EventoSanitarioCreate, EventoSanitarioUpdate
from app.modules.sanidad.service import SanidadService

router = APIRouter(prefix="/sanidad", tags=["Sanidad"])


@router.get("")
async def list_sanidad(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await SanidadService.list(db)
    return success_response(
        message="Eventos sanitarios obtenidos",
        data=[item.model_dump() for item in data],
    )


@router.get("/historial/{lote_id}")
async def historial_sanidad(
    lote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await SanidadService.historial_por_lote(db, lote_id)
    return success_response(
        message="Historial sanitario del lote obtenido",
        data=[item.model_dump() for item in data],
    )


@router.get("/{evento_id}")
async def get_sanidad(
    evento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await SanidadService.get_by_id(db, evento_id)
    return success_response(message="Evento sanitario obtenido", data=data.model_dump())


@router.post("")
async def create_sanidad(
    payload: EventoSanitarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await SanidadService.create(db, payload)
    return success_response(message="Evento sanitario creado", data=data.model_dump())


@router.put("/{evento_id}")
async def update_sanidad(
    evento_id: str,
    payload: EventoSanitarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await SanidadService.update(db, evento_id, payload)
    return success_response(
        message="Evento sanitario actualizado", data=data.model_dump()
    )


@router.delete("/{evento_id}")
async def delete_sanidad(
    evento_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    await SanidadService.delete(db, evento_id)
    return success_response(message="Evento sanitario eliminado", data=None)

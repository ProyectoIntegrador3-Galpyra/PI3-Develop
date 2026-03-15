from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.responses import success_response
from app.modules.galpones.schemas import GalponCreate, GalponUpdate
from app.modules.galpones.service import GalponService

router = APIRouter(prefix="/galpones", tags=["Galpones"])


@router.get("")
async def list_galpones(db: AsyncSession = Depends(get_db)) -> dict:
    # Seguridad desactivada en modo desarrollo abierto.
    data = await GalponService.list(db)
    return success_response(
        message="Galpones obtenidos",
        data=[item.model_dump() for item in data],
    )


@router.get("/{galpon_id}")
async def get_galpon(galpon_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    data = await GalponService.get_by_id(db, galpon_id)
    return success_response(message="Galpon obtenido", data=data.model_dump())


@router.post("")
async def create_galpon(payload: GalponCreate, db: AsyncSession = Depends(get_db)) -> dict:
    data = await GalponService.create(db, payload)
    return success_response(message="Galpon creado", data=data.model_dump())


@router.put("/{galpon_id}")
async def update_galpon(
    galpon_id: str,
    payload: GalponUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    data = await GalponService.update(db, galpon_id, payload)
    return success_response(message="Galpon actualizado", data=data.model_dump())


@router.delete("/{galpon_id}")
async def delete_galpon(galpon_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    await GalponService.delete(db, galpon_id)
    return success_response(message="Galpon eliminado", data=None)

# CORRECCIÓN APLICADA: [1 — Autenticación en endpoints]
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.modules.auth.models import Usuario
from app.modules.inventario_foto.schemas import InventarioConfirmarRequest
from app.modules.inventario_foto.service import InventarioFotoService

router = APIRouter(prefix="/inventario", tags=["Inventario Foto"])


@router.post("/procesar")
async def procesar_inventario_foto(
    file: UploadFile = File(...),
    lote_id: str | None = Form(default=None),
    galpon_id: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await InventarioFotoService.procesar_imagen(db, file, lote_id, galpon_id)
    return success_response(message="Imagen procesada", data=data.model_dump())


@router.post("/confirmar")
async def confirmar_inventario_foto(
    payload: InventarioConfirmarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await InventarioFotoService.confirmar_conteo(db, payload)
    return success_response(message="Conteo confirmado", data=data.model_dump())


@router.get("/jobs")
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await InventarioFotoService.list_jobs(db)
    return success_response(
        message="Jobs de inventario obtenidos",
        data=[item.model_dump() for item in data],
    )


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await InventarioFotoService.get_job(db, job_id)
    return success_response(
        message="Job de inventario obtenido", data=data.model_dump()
    )

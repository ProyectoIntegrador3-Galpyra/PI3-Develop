# CORRECCIÓN APLICADA: [1 — Autenticación en endpoints]
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.modules.auth.models import Usuario
from app.modules.reportes.schemas import ReporteGenerarRequest
from app.modules.reportes.service import ReportesService

router = APIRouter(prefix="/reportes", tags=["Reportes"])


def _reporte_payload(item) -> dict:
    payload = item.model_dump()
    payload["url_reporte"] = payload.get("url_archivo")
    return payload


@router.get(
    "",
    summary="Listar reportes",
    description="Retorna los reportes generados y disponibles.",
)
async def list_reportes(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await ReportesService.list(db)
    return success_response(
        message="Reportes obtenidos",
        data=[_reporte_payload(item) for item in data],
    )


@router.get(
    "/{reporte_id}",
    summary="Obtener reporte",
    description="Retorna el detalle de un reporte generado.",
)
async def get_reporte(
    reporte_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await ReportesService.get_by_id(db, reporte_id)
    return success_response(message="Reporte obtenido", data=_reporte_payload(data))


@router.post(
    "/generar",
    summary="Generar reporte",
    description="Genera un reporte PDF y registra su ubicación.",
)
async def generar_reporte(
    payload: ReporteGenerarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await ReportesService.generar(db, payload)
    return success_response(message="Reporte generado", data=_reporte_payload(data))

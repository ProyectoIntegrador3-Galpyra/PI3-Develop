from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.responses import success_response
from app.modules.reportes.schemas import ReporteGenerarRequest
from app.modules.reportes.service import ReportesService

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("")
async def list_reportes(db: AsyncSession = Depends(get_db)) -> dict:
    # Seguridad desactivada en modo desarrollo abierto.
    data = await ReportesService.list(db)
    return success_response(
        message="Reportes obtenidos",
        data=[item.model_dump() for item in data],
    )


@router.get("/{reporte_id}")
async def get_reporte(reporte_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    data = await ReportesService.get_by_id(db, reporte_id)
    return success_response(message="Reporte obtenido", data=data.model_dump())


@router.post("/generar")
async def generar_reporte(
    payload: ReporteGenerarRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    data = await ReportesService.generar(db, payload)
    return success_response(message="Reporte generado", data=data.model_dump())

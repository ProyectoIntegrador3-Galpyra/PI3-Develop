from datetime import datetime, timezone

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.modules.reportes.models import ReporteGenerado
from app.modules.reportes.schemas import ReporteGenerarRequest, ReporteOut


class ReportesService:
    @staticmethod
    async def list(db: AsyncSession) -> list[ReporteOut]:
        result = await db.execute(
            select(ReporteGenerado)
            .where(ReporteGenerado.deleted_at.is_(None))
            .order_by(ReporteGenerado.created_at.desc())
        )
        return [ReporteOut.model_validate(item) for item in result.scalars().all()]

    @staticmethod
    async def get_by_id(db: AsyncSession, reporte_id: str) -> ReporteOut:
        result = await db.execute(
            select(ReporteGenerado).where(
                ReporteGenerado.id == reporte_id,
                ReporteGenerado.deleted_at.is_(None),
            )
        )
        reporte = result.scalar_one_or_none()
        if reporte is None:
            raise AppException(
                message="Reporte no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return ReporteOut.model_validate(reporte)

    @staticmethod
    async def generar(db: AsyncSession, payload: ReporteGenerarRequest) -> ReporteOut:
        timestamp = int(datetime.now(timezone.utc).timestamp())
        reporte = ReporteGenerado(
            tipo=payload.tipo,
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
            formato=payload.formato,
            url_archivo=f"/reportes/{payload.tipo}_{timestamp}.{payload.formato.lower()}",
            generado_por=payload.generado_por,
        )

        db.add(reporte)
        await db.commit()
        await db.refresh(reporte)
        return ReporteOut.model_validate(reporte)

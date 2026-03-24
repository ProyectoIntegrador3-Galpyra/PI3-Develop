# CORRECCIÓN APLICADA: Reportes S3
import asyncio
import logging
import os
import re
import tempfile
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError
from fastapi import status
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException
from app.modules.reportes.models import ReporteGenerado
from app.modules.reportes.schemas import ReporteGenerarRequest, ReporteOut

logger = logging.getLogger(__name__)


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
        tipo_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", payload.tipo)
        formato_safe = re.sub(r"[^a-zA-Z0-9]", "", payload.formato).lower()

        url_archivo = f"/reportes/{tipo_safe}_{timestamp}.{formato_safe}"
        if payload.formato.upper() == "PDF":
            with tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False,
                prefix=f"reporte_{tipo_safe}_{timestamp}_",
            ) as tmp_file:
                ruta_tmp = tmp_file.name

            def build_pdf() -> None:
                pdf = canvas.Canvas(ruta_tmp, pagesize=A4)
                pdf.setTitle(f"Reporte {payload.tipo}")
                pdf.setFont("Helvetica-Bold", 16)
                pdf.drawString(72, 800, f"Reporte {payload.tipo}")
                pdf.setFont("Helvetica", 12)
                pdf.drawString(
                    72,
                    770,
                    f"Período: {payload.fecha_inicio.date()} — {payload.fecha_fin.date()}",
                )
                pdf.drawString(
                    72,
                    740,
                    (
                        "Generado: "
                        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
                    ),
                )
                pdf.save()

            await asyncio.to_thread(build_pdf)

            if settings.environment == "development":
                url_archivo = ruta_tmp
            else:
                reporte_id = f"{tipo_safe}_{timestamp}"
                s3_key = f"reportes/{reporte_id}.pdf"
                try:
                    def upload_to_s3() -> str:
                        s3 = boto3.client(
                            "s3",
                            region_name=settings.aws_region,
                        )
                        s3.upload_file(ruta_tmp, settings.aws_s3_bucket, s3_key)
                        presigned_url = s3.generate_presigned_url(
                            "get_object",
                            Params={"Bucket": settings.aws_s3_bucket, "Key": s3_key},
                            ExpiresIn=86400,
                        )
                        return presigned_url

                    url_archivo = await asyncio.to_thread(upload_to_s3)
                    try:
                        os.unlink(ruta_tmp)
                    except OSError:
                        pass
                except ClientError as exc:
                    logger.error("Error al subir reporte a S3: %s", exc)
                    url_archivo = ruta_tmp

        reporte = ReporteGenerado(
            tipo=payload.tipo,
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
            formato=payload.formato,
            url_archivo=url_archivo,
            generado_por=payload.generado_por,
        )

        db.add(reporte)
        await db.commit()
        await db.refresh(reporte)
        return ReporteOut.model_validate(reporte)

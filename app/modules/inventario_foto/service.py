import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger(__name__)

from fastapi import UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException
from app.modules.inventario_foto.models import InventarioFotoJob
from app.modules.inventario_foto.schemas import (InventarioConfirmarRequest,
                                                 InventarioFotoJobOut,
                                                 InventarioProcesarResponse)
from app.shared.enums import EstadoInventarioFoto


class InventarioFotoService:
    @staticmethod
    async def procesar_imagen(
        db: AsyncSession,
        file: UploadFile,
        lote_id: str | None,
        galpon_id: str | None,
    ) -> InventarioProcesarResponse:
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = f"{uuid4()}_{file.filename or 'inventario.jpg'}"
        file_path = upload_dir / safe_filename

        with file_path.open("wb") as out_file:
            shutil.copyfileobj(file.file, out_file)

        conteo = settings.simulated_inventory_count
        bounding_boxes: list[dict] = []
        modo = "cloud"

        try:
            from ultralytics import YOLO  # type: ignore

            model_path = Path("app/models/yolov8n.pt")
            if model_path.exists() and model_path.stat().st_size > 1000:
                model = YOLO(str(model_path))
                results = model.predict(source=str(file_path), verbose=False)
                if results:
                    boxes = results[0].boxes
                    conteo = len(boxes)
                    bounding_boxes = []
                    for box in boxes:
                        xyxy = box.xyxy.tolist()[0]
                        bounding_boxes.append(
                            {
                                "x1": float(xyxy[0]),
                                "y1": float(xyxy[1]),
                                "x2": float(xyxy[2]),
                                "y2": float(xyxy[3]),
                            }
                        )
        except Exception as exc:  # noqa: BLE001
            # Si ultralytics no esta instalado o falla el modelo, se usa conteo simulado.
            logger.warning(
                "Inferencia YOLOv8n no disponible, usando conteo simulado: %s", exc
            )
            conteo = settings.simulated_inventory_count
            bounding_boxes = []

        job = InventarioFotoJob(
            lote_id=lote_id,
            galpon_id=galpon_id,
            image_url=str(file_path).replace("\\", "/"),
            filename=safe_filename,
            conteo_estimado=conteo,
            origen=modo,
            estado=EstadoInventarioFoto.PROCESADO,
            bounding_boxes_json=bounding_boxes,
            procesado_en=datetime.now(timezone.utc),
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        return InventarioProcesarResponse(
            conteo=conteo,
            bounding_boxes=bounding_boxes,
            job_id=job.id,
            modo=modo,
        )

    @staticmethod
    async def confirmar_conteo(
        db: AsyncSession,
        payload: InventarioConfirmarRequest,
    ) -> InventarioFotoJobOut:
        result = await db.execute(
            select(InventarioFotoJob).where(
                InventarioFotoJob.id == payload.job_id,
                InventarioFotoJob.deleted_at.is_(None),
            )
        )
        job = result.scalar_one_or_none()
        if job is None:
            raise AppException(
                message="Job de inventario no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        job.conteo_confirmado = payload.conteo_confirmado
        job.lote_id = payload.lote_id or job.lote_id
        job.galpon_id = payload.galpon_id or job.galpon_id
        job.estado = EstadoInventarioFoto.CONFIRMADO
        job.confirmado_en = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(job)

        return InventarioFotoJobOut.model_validate(job)

    @staticmethod
    async def list_jobs(db: AsyncSession) -> list[InventarioFotoJobOut]:
        result = await db.execute(
            select(InventarioFotoJob)
            .where(InventarioFotoJob.deleted_at.is_(None))
            .order_by(InventarioFotoJob.created_at.desc())
        )
        return [
            InventarioFotoJobOut.model_validate(item) for item in result.scalars().all()
        ]

    @staticmethod
    async def get_job(db: AsyncSession, job_id: str) -> InventarioFotoJobOut:
        result = await db.execute(
            select(InventarioFotoJob).where(
                InventarioFotoJob.id == job_id,
                InventarioFotoJob.deleted_at.is_(None),
            )
        )
        job = result.scalar_one_or_none()
        if job is None:
            raise AppException(
                message="Job de inventario no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return InventarioFotoJobOut.model_validate(job)

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.modules.aves.models import LoteAve, MovimientoAve
from app.modules.produccion.models import ProduccionHuevo
from app.modules.sync.models import SyncLog
from app.modules.sync.schemas import (
    SyncLogOut,
    SyncOperation,
    SyncOperationResult,
    SyncRequest,
    SyncResponse,
)
from app.shared.enums import EstadoSync, TipoMovimientoAve
from app.shared.utils import parse_datetime, update_model_from_dict


class SyncService:
    @staticmethod
    async def procesar_batch(db: AsyncSession, payload: SyncRequest) -> SyncResponse:
        procesadas = 0
        fallidas = 0
        detalles: list[SyncOperationResult] = []

        for operation in payload.operaciones:
            log = SyncLog(
                operacion=operation.operacion,
                entidad=operation.entidad,
                entidad_id=operation.payload.get("id", operation.id),
                payload_json=operation.payload,
                cliente_created_at=operation.created_at,
                estado=EstadoSync.PENDIENTE,
            )
            db.add(log)
            await db.flush()

            try:
                if operation.entidad in {"produccion_huevos", "produccion"}:
                    message = await SyncService._upsert_produccion(db, operation)
                elif operation.entidad in {"movimiento_aves", "movimientos_aves"}:
                    message = await SyncService._upsert_movimiento(db, operation)
                else:
                    raise AppException(
                        message=(
                            f"Entidad {operation.entidad} no soportada en esta fase. "
                            "Implementado: produccion_huevos y movimiento_aves."
                        )
                    )

                log.estado = EstadoSync.PROCESADO
                log.mensaje = message
                log.procesado_at = datetime.now(timezone.utc)
                procesadas += 1
                detalles.append(
                    SyncOperationResult(
                        id=operation.id,
                        entidad=operation.entidad,
                        estado=EstadoSync.PROCESADO,
                        mensaje=message,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                log.estado = EstadoSync.ERROR
                log.mensaje = str(exc)
                log.procesado_at = datetime.now(timezone.utc)
                fallidas += 1
                detalles.append(
                    SyncOperationResult(
                        id=operation.id,
                        entidad=operation.entidad,
                        estado=EstadoSync.ERROR,
                        mensaje=str(exc),
                    )
                )

        await db.commit()

        return SyncResponse(procesadas=procesadas, fallidas=fallidas, detalles=detalles)

    @staticmethod
    async def list_logs(db: AsyncSession) -> list[SyncLogOut]:
        result = await db.execute(
            select(SyncLog)
            .where(SyncLog.deleted_at.is_(None))
            .order_by(SyncLog.created_at.desc())
        )
        return [SyncLogOut.model_validate(item) for item in result.scalars().all()]

    @staticmethod
    async def _upsert_produccion(db: AsyncSession, operation: SyncOperation) -> str:
        data = dict(operation.payload)
        entity_id = data.get("id", operation.id)
        payload_updated_at = parse_datetime(data.get("updated_at")) or operation.created_at

        result = await db.execute(
            select(ProduccionHuevo).where(ProduccionHuevo.id == entity_id)
        )
        row = result.scalar_one_or_none()

        if row is None:
            required_fields = ["galpon_id", "fecha", "cantidad"]
            missing = [field for field in required_fields if field not in data]
            if missing:
                raise AppException(message=f"Faltan campos requeridos: {', '.join(missing)}")

            row = ProduccionHuevo(
                id=entity_id,
                galpon_id=data["galpon_id"],
                lote_id=data.get("lote_id"),
                fecha=parse_datetime(data["fecha"]),
                cantidad=int(data["cantidad"]),
                huevos_rotos=data.get("huevos_rotos"),
                observaciones=data.get("observaciones"),
            )
            db.add(row)
            return "Creado por sync"

        current_updated_at = row.updated_at
        if current_updated_at.tzinfo is None:
            current_updated_at = current_updated_at.replace(tzinfo=timezone.utc)

        if payload_updated_at <= current_updated_at:
            return "Descartado por Last Write Wins"

        update_data = {
            "galpon_id": data.get("galpon_id", row.galpon_id),
            "lote_id": data.get("lote_id", row.lote_id),
            "fecha": parse_datetime(data.get("fecha")) or row.fecha,
            "cantidad": int(data.get("cantidad", row.cantidad)),
            "huevos_rotos": data.get("huevos_rotos", row.huevos_rotos),
            "observaciones": data.get("observaciones", row.observaciones),
        }
        update_model_from_dict(row, update_data)
        return "Actualizado por sync"

    @staticmethod
    async def _upsert_movimiento(db: AsyncSession, operation: SyncOperation) -> str:
        data = dict(operation.payload)
        entity_id = data.get("id", operation.id)
        payload_updated_at = parse_datetime(data.get("updated_at")) or operation.created_at

        result = await db.execute(
            select(MovimientoAve).where(MovimientoAve.id == entity_id)
        )
        row = result.scalar_one_or_none()

        if row is None:
            required_fields = ["lote_id", "tipo_movimiento", "cantidad", "causa", "fecha"]
            missing = [field for field in required_fields if field not in data]
            if missing:
                raise AppException(message=f"Faltan campos requeridos: {', '.join(missing)}")

            lote_result = await db.execute(select(LoteAve).where(LoteAve.id == data["lote_id"]))
            lote = lote_result.scalar_one_or_none()
            if lote is None:
                raise AppException(message="Lote no encontrado para sync de movimiento")

            tipo = TipoMovimientoAve(data["tipo_movimiento"])
            cantidad = int(data["cantidad"])

            if tipo == TipoMovimientoAve.MORTALIDAD:
                if lote.cantidad_actual < cantidad:
                    raise AppException(message="Mortalidad sync supera cantidad actual")
                lote.cantidad_actual -= cantidad
            elif tipo == TipoMovimientoAve.INGRESO:
                lote.cantidad_actual += cantidad
            else:
                lote.cantidad_actual += cantidad

            row = MovimientoAve(
                id=entity_id,
                lote_id=data["lote_id"],
                tipo_movimiento=tipo,
                cantidad=cantidad,
                causa=data["causa"],
                fecha=parse_datetime(data["fecha"]),
                observaciones=data.get("observaciones"),
            )
            db.add(row)
            return "Movimiento creado por sync"

        current_updated_at = row.updated_at
        if current_updated_at.tzinfo is None:
            current_updated_at = current_updated_at.replace(tzinfo=timezone.utc)

        if payload_updated_at <= current_updated_at:
            return "Descartado por Last Write Wins"

        update_data = {
            "tipo_movimiento": TipoMovimientoAve(
                data.get("tipo_movimiento", row.tipo_movimiento.value)
            ),
            "cantidad": int(data.get("cantidad", row.cantidad)),
            "causa": data.get("causa", row.causa),
            "fecha": parse_datetime(data.get("fecha")) or row.fecha,
            "observaciones": data.get("observaciones", row.observaciones),
        }
        update_model_from_dict(row, update_data)
        return "Movimiento actualizado por sync"

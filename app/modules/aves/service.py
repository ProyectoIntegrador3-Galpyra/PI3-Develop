from datetime import datetime, timezone

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.modules.aves.models import LoteAve, MovimientoAve
from app.modules.aves.schemas import (
    LoteAveCreate,
    LoteAveOut,
    LoteAveUpdate,
    MovimientoAveCreate,
    MovimientoAveOut,
)
from app.shared.enums import TipoMovimientoAve


class AvesService:
    @staticmethod
    async def list_lotes(db: AsyncSession) -> list[LoteAveOut]:
        result = await db.execute(
            select(LoteAve)
            .where(LoteAve.deleted_at.is_(None))
            .order_by(LoteAve.created_at.desc())
        )
        return [LoteAveOut.model_validate(item) for item in result.scalars().all()]

    @staticmethod
    async def list_lotes_por_galpon(
        db: AsyncSession,
        galpon_id: str,
    ) -> list[LoteAveOut]:
        result = await db.execute(
            select(LoteAve)
            .where(
                LoteAve.galpon_id == galpon_id,
                LoteAve.deleted_at.is_(None),
            )
            .order_by(LoteAve.created_at.desc())
        )
        return [LoteAveOut.model_validate(item) for item in result.scalars().all()]

    @staticmethod
    async def get_lote(db: AsyncSession, lote_id: str) -> LoteAveOut:
        result = await db.execute(
            select(LoteAve).where(LoteAve.id == lote_id, LoteAve.deleted_at.is_(None))
        )
        lote = result.scalar_one_or_none()
        if lote is None:
            raise AppException(
                message="Lote no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return LoteAveOut.model_validate(lote)

    @staticmethod
    async def create_lote(db: AsyncSession, payload: LoteAveCreate) -> LoteAveOut:
        data = payload.model_dump()
        if data.get("cantidad_actual") is None:
            data["cantidad_actual"] = payload.cantidad_inicial

        lote = LoteAve(**data)
        db.add(lote)
        await db.commit()
        await db.refresh(lote)
        return LoteAveOut.model_validate(lote)

    @staticmethod
    async def update_lote(
        db: AsyncSession,
        lote_id: str,
        payload: LoteAveUpdate,
    ) -> LoteAveOut:
        result = await db.execute(
            select(LoteAve).where(LoteAve.id == lote_id, LoteAve.deleted_at.is_(None))
        )
        lote = result.scalar_one_or_none()
        if lote is None:
            raise AppException(
                message="Lote no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(lote, field, value)

        await db.commit()
        await db.refresh(lote)
        return LoteAveOut.model_validate(lote)

    @staticmethod
    async def delete_lote(db: AsyncSession, lote_id: str) -> None:
        result = await db.execute(
            select(LoteAve).where(LoteAve.id == lote_id, LoteAve.deleted_at.is_(None))
        )
        lote = result.scalar_one_or_none()
        if lote is None:
            raise AppException(
                message="Lote no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        lote.deleted_at = datetime.now(timezone.utc)
        await db.commit()

    @staticmethod
    async def registrar_movimiento(
        db: AsyncSession,
        payload: MovimientoAveCreate,
        tipo_forzado: TipoMovimientoAve | None = None,
    ) -> MovimientoAveOut:
        result = await db.execute(
            select(LoteAve).where(LoteAve.id == payload.lote_id, LoteAve.deleted_at.is_(None))
        )
        lote = result.scalar_one_or_none()
        if lote is None:
            raise AppException(
                message="Lote no encontrado para movimiento",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        tipo_movimiento = tipo_forzado or payload.tipo_movimiento

        if tipo_movimiento == TipoMovimientoAve.MORTALIDAD:
            if lote.cantidad_actual < payload.cantidad:
                raise AppException(message="La mortalidad supera la cantidad actual del lote")
            lote.cantidad_actual -= payload.cantidad
        elif tipo_movimiento == TipoMovimientoAve.INGRESO:
            lote.cantidad_actual += payload.cantidad
        else:
            lote.cantidad_actual += payload.cantidad

        movimiento = MovimientoAve(
            lote_id=payload.lote_id,
            tipo_movimiento=tipo_movimiento,
            cantidad=payload.cantidad,
            causa=payload.causa,
            fecha=payload.fecha,
            observaciones=payload.observaciones,
        )

        db.add(movimiento)
        await db.commit()
        await db.refresh(movimiento)
        return MovimientoAveOut.model_validate(movimiento)

from datetime import datetime, timezone

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.modules.produccion.models import ProduccionHuevo
from app.modules.produccion.schemas import ProduccionCreate, ProduccionOut, ProduccionUpdate


class ProduccionService:
    @staticmethod
    async def list(db: AsyncSession) -> list[ProduccionOut]:
        result = await db.execute(
            select(ProduccionHuevo)
            .where(ProduccionHuevo.deleted_at.is_(None))
            .order_by(ProduccionHuevo.fecha.desc())
        )
        return [ProduccionOut.model_validate(item) for item in result.scalars().all()]

    @staticmethod
    async def get_by_id(db: AsyncSession, produccion_id: str) -> ProduccionOut:
        result = await db.execute(
            select(ProduccionHuevo).where(
                ProduccionHuevo.id == produccion_id,
                ProduccionHuevo.deleted_at.is_(None),
            )
        )
        produccion = result.scalar_one_or_none()
        if produccion is None:
            raise AppException(
                message="Registro de produccion no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return ProduccionOut.model_validate(produccion)

    @staticmethod
    async def create(db: AsyncSession, payload: ProduccionCreate) -> ProduccionOut:
        row = ProduccionHuevo(**payload.model_dump())
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return ProduccionOut.model_validate(row)

    @staticmethod
    async def update(
        db: AsyncSession,
        produccion_id: str,
        payload: ProduccionUpdate,
    ) -> ProduccionOut:
        result = await db.execute(
            select(ProduccionHuevo).where(
                ProduccionHuevo.id == produccion_id,
                ProduccionHuevo.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise AppException(
                message="Registro de produccion no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(row, field, value)

        await db.commit()
        await db.refresh(row)
        return ProduccionOut.model_validate(row)

    @staticmethod
    async def delete(db: AsyncSession, produccion_id: str) -> None:
        result = await db.execute(
            select(ProduccionHuevo).where(
                ProduccionHuevo.id == produccion_id,
                ProduccionHuevo.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise AppException(
                message="Registro de produccion no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        row.deleted_at = datetime.now(timezone.utc)
        await db.commit()

    @staticmethod
    async def list_rango(
        db: AsyncSession,
        fecha_inicio: datetime,
        fecha_fin: datetime,
    ) -> list[ProduccionOut]:
        result = await db.execute(
            select(ProduccionHuevo)
            .where(
                ProduccionHuevo.deleted_at.is_(None),
                ProduccionHuevo.fecha >= fecha_inicio,
                ProduccionHuevo.fecha <= fecha_fin,
            )
            .order_by(ProduccionHuevo.fecha.desc())
        )
        return [ProduccionOut.model_validate(item) for item in result.scalars().all()]

    @staticmethod
    async def list_por_galpon(db: AsyncSession, galpon_id: str) -> list[ProduccionOut]:
        result = await db.execute(
            select(ProduccionHuevo)
            .where(
                ProduccionHuevo.galpon_id == galpon_id,
                ProduccionHuevo.deleted_at.is_(None),
            )
            .order_by(ProduccionHuevo.fecha.desc())
        )
        return [ProduccionOut.model_validate(item) for item in result.scalars().all()]

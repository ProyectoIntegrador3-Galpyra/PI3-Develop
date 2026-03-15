from datetime import datetime, timezone

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.modules.alimentacion.models import AlimentacionRegistro
from app.modules.alimentacion.schemas import (
    AlimentacionCreate,
    AlimentacionOut,
    AlimentacionUpdate,
)


class AlimentacionService:
    @staticmethod
    async def list(db: AsyncSession) -> list[AlimentacionOut]:
        result = await db.execute(
            select(AlimentacionRegistro)
            .where(AlimentacionRegistro.deleted_at.is_(None))
            .order_by(AlimentacionRegistro.fecha.desc())
        )
        return [AlimentacionOut.model_validate(item) for item in result.scalars().all()]

    @staticmethod
    async def get_by_id(db: AsyncSession, registro_id: str) -> AlimentacionOut:
        result = await db.execute(
            select(AlimentacionRegistro).where(
                AlimentacionRegistro.id == registro_id,
                AlimentacionRegistro.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise AppException(
                message="Registro de alimentacion no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return AlimentacionOut.model_validate(row)

    @staticmethod
    async def create(db: AsyncSession, payload: AlimentacionCreate) -> AlimentacionOut:
        row = AlimentacionRegistro(**payload.model_dump())
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return AlimentacionOut.model_validate(row)

    @staticmethod
    async def update(
        db: AsyncSession,
        registro_id: str,
        payload: AlimentacionUpdate,
    ) -> AlimentacionOut:
        result = await db.execute(
            select(AlimentacionRegistro).where(
                AlimentacionRegistro.id == registro_id,
                AlimentacionRegistro.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise AppException(
                message="Registro de alimentacion no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(row, field, value)

        await db.commit()
        await db.refresh(row)
        return AlimentacionOut.model_validate(row)

    @staticmethod
    async def delete(db: AsyncSession, registro_id: str) -> None:
        result = await db.execute(
            select(AlimentacionRegistro).where(
                AlimentacionRegistro.id == registro_id,
                AlimentacionRegistro.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise AppException(
                message="Registro de alimentacion no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        row.deleted_at = datetime.now(timezone.utc)
        await db.commit()

    @staticmethod
    async def list_rango(
        db: AsyncSession,
        fecha_inicio: datetime,
        fecha_fin: datetime,
    ) -> list[AlimentacionOut]:
        result = await db.execute(
            select(AlimentacionRegistro)
            .where(
                AlimentacionRegistro.deleted_at.is_(None),
                AlimentacionRegistro.fecha >= fecha_inicio,
                AlimentacionRegistro.fecha <= fecha_fin,
            )
            .order_by(AlimentacionRegistro.fecha.desc())
        )
        return [AlimentacionOut.model_validate(item) for item in result.scalars().all()]

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.aves.models import LoteAve, MovimientoAve
from app.modules.produccion.models import ProduccionHuevo
from app.shared.enums import EstadoLote, TipoMovimientoAve


class DashboardService:

    @staticmethod
    async def get_metrics(db: AsyncSession) -> dict:
        # 1. Total aves activas
        result = await db.execute(
            select(func.sum(LoteAve.cantidad_actual)).where(
                LoteAve.deleted_at.is_(None),
                LoteAve.estado == EstadoLote.ACTIVO,
            )
        )
        total_aves = result.scalar() or 0

        # 2. Producción últimos 7 días
        hace_7_dias = datetime.now(timezone.utc) - timedelta(days=7)
        result = await db.execute(
            select(func.sum(ProduccionHuevo.cantidad)).where(
                ProduccionHuevo.deleted_at.is_(None),
                ProduccionHuevo.fecha >= hace_7_dias,
            )
        )
        produccion_7d = result.scalar() or 0

        # 3. Tasa de mortalidad
        result_bajas = await db.execute(
            select(func.sum(MovimientoAve.cantidad)).where(
                MovimientoAve.deleted_at.is_(None),
                MovimientoAve.tipo_movimiento == TipoMovimientoAve.MORTALIDAD,
            )
        )
        total_bajas = result_bajas.scalar() or 0

        result_inicial = await db.execute(
            select(func.sum(LoteAve.cantidad_inicial)).where(
                LoteAve.deleted_at.is_(None),
            )
        )
        total_inicial = result_inicial.scalar() or 0

        tasa = (
            round((total_bajas / total_inicial) * 100, 2) if total_inicial > 0 else 0.0
        )

        # 4. Alertas: lotes activos sin aves
        result_alertas = await db.execute(
            select(LoteAve.codigo_lote).where(
                LoteAve.deleted_at.is_(None),
                LoteAve.estado == EstadoLote.ACTIVO,
                LoteAve.cantidad_actual == 0,
            )
        )
        codigos_vacios = result_alertas.scalars().all()
        alertas = [f"Lote {c} sin aves activas" for c in codigos_vacios]

        return {
            "total_aves_activas": total_aves,
            "produccion_ultimos_7_dias": produccion_7d,
            "tasa_mortalidad_porcentaje": tasa,
            "alertas": alertas,
        }

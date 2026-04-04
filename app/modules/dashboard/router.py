# CORRECCIÓN APLICADA: [1 — Autenticación en endpoints]
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.modules.auth.models import Usuario
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "",
    summary="Obtener dashboard",
    description="Retorna las métricas principales del sistema en tiempo real.",
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    data = await DashboardService.get_metrics(db)
    return success_response(message="Métricas del dashboard obtenidas", data=data)

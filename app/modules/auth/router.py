from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.responses import success_response
from app.modules.auth.schemas import (LoginRequest, LogoutRequest,
                                      RefreshRequest)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    summary="Iniciar sesión",
    description="Autentica al usuario y retorna access token y refresh token.",
)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict:
    data = await AuthService.login(db, payload)
    return success_response(message="Login exitoso", data=data.model_dump())


@router.post(
    "/refresh",
    summary="Refrescar token",
    description="Genera un nuevo access token usando el refresh token.",
)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> dict:
    data = await AuthService.refresh(db, payload)
    return success_response(message="Token refrescado", data=data.model_dump())


@router.post(
    "/logout",
    summary="Cerrar sesión",
    description="Invalida el refresh token del usuario.",
)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)) -> dict:
    await AuthService.logout(db, payload)
    return success_response(message="Sesion cerrada", data=None)


@router.get(
    "/me",
    summary="Perfil del usuario",
    description="Retorna los datos del usuario autenticado.",
)
async def me(
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> dict:
    # Seguridad desactivada en modo desarrollo abierto.
    # Para produccion, agregar Depends(get_current_user) en los endpoints protegidos.
    bearer_token: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        bearer_token = authorization.split(" ", 1)[1]

    user = await AuthService.me(db, bearer_token)
    return success_response(message="Perfil obtenido", data=user.model_dump())

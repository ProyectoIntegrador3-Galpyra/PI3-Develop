from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.responses import success_response
from app.modules.alimentacion.router import router as alimentacion_router
from app.modules.auth.router import router as auth_router
from app.modules.aves.router import router as aves_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.galpones.router import router as galpones_router
from app.modules.inventario_foto.router import router as inventario_router
from app.modules.produccion.router import router as produccion_router
from app.modules.reportes.router import router as reportes_router
from app.modules.sanidad.router import router as sanidad_router
from app.modules.sync.router import router as sync_router
from app.modules.trazabilidad.router import router as trazabilidad_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="GALPyra API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_router = APIRouter(prefix="/api")

    @api_router.get("/health", tags=["Health"])
    async def health() -> dict:
        return success_response(
            message="Servicio saludable",
            data={"status": "ok", "environment": settings.environment},
        )

    api_router.include_router(auth_router)
    api_router.include_router(galpones_router)
    api_router.include_router(aves_router)
    api_router.include_router(produccion_router)
    api_router.include_router(sanidad_router)
    api_router.include_router(alimentacion_router)
    api_router.include_router(reportes_router)
    api_router.include_router(sync_router)
    api_router.include_router(inventario_router)
    api_router.include_router(dashboard_router)
    api_router.include_router(trazabilidad_router)

    app.include_router(api_router)
    register_exception_handlers(app)

    return app


app = create_app()

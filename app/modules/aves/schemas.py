from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import EstadoLote, TipoMovimientoAve


class LoteAveBase(BaseModel):
    codigo_lote: str = Field(min_length=1, max_length=80)
    tipo_ave: str = Field(min_length=1, max_length=80)
    raza: str = Field(min_length=1, max_length=120)
    cantidad_inicial: int = Field(gt=0)
    fecha_ingreso: datetime
    galpon_id: str = Field(min_length=36, max_length=36)
    estado: EstadoLote = EstadoLote.ACTIVO


class LoteAveCreate(LoteAveBase):
    cantidad_actual: int | None = Field(default=None, ge=0)


class LoteAveUpdate(BaseModel):
    tipo_ave: str | None = Field(default=None, min_length=1, max_length=80)
    raza: str | None = Field(default=None, min_length=1, max_length=120)
    cantidad_actual: int | None = Field(default=None, ge=0)
    estado: EstadoLote | None = None


class LoteAveOut(LoteAveBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cantidad_actual: int
    created_at: datetime
    updated_at: datetime


class MovimientoAveBase(BaseModel):
    lote_id: str = Field(min_length=36, max_length=36)
    cantidad: int = Field(gt=0)
    causa: str = Field(min_length=1, max_length=120)
    fecha: datetime
    observaciones: str | None = None


class MovimientoAveCreate(MovimientoAveBase):
    tipo_movimiento: TipoMovimientoAve = TipoMovimientoAve.AJUSTE


class MovimientoIngresoCreate(MovimientoAveBase):
    pass


class MovimientoMortalidadCreate(MovimientoAveBase):
    pass


class MovimientoAveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lote_id: str
    tipo_movimiento: TipoMovimientoAve
    cantidad: int
    causa: str
    fecha: datetime
    observaciones: str | None
    created_at: datetime
    updated_at: datetime

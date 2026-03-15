from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlimentacionBase(BaseModel):
    galpon_id: str = Field(min_length=36, max_length=36)
    lote_id: str | None = Field(default=None, min_length=36, max_length=36)
    fecha: datetime
    tipo_alimento: str = Field(min_length=1, max_length=120)
    cantidad_kg: float = Field(gt=0)
    costo: float | None = Field(default=None, ge=0)
    observaciones: str | None = None


class AlimentacionCreate(AlimentacionBase):
    pass


class AlimentacionUpdate(BaseModel):
    fecha: datetime | None = None
    tipo_alimento: str | None = Field(default=None, min_length=1, max_length=120)
    cantidad_kg: float | None = Field(default=None, gt=0)
    costo: float | None = Field(default=None, ge=0)
    observaciones: str | None = None


class AlimentacionOut(AlimentacionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime

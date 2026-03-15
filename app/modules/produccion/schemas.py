from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProduccionBase(BaseModel):
    galpon_id: str = Field(min_length=36, max_length=36)
    lote_id: str | None = Field(default=None, min_length=36, max_length=36)
    fecha: datetime
    cantidad: int = Field(ge=0)
    huevos_rotos: int | None = Field(default=None, ge=0)
    observaciones: str | None = None


class ProduccionCreate(ProduccionBase):
    pass


class ProduccionUpdate(BaseModel):
    galpon_id: str | None = Field(default=None, min_length=36, max_length=36)
    lote_id: str | None = Field(default=None, min_length=36, max_length=36)
    fecha: datetime | None = None
    cantidad: int | None = Field(default=None, ge=0)
    huevos_rotos: int | None = Field(default=None, ge=0)
    observaciones: str | None = None


class ProduccionOut(ProduccionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import TipoEventoSanitario


class EventoSanitarioBase(BaseModel):
    lote_id: str = Field(min_length=36, max_length=36)
    galpon_id: str = Field(min_length=36, max_length=36)
    tipo_evento: TipoEventoSanitario
    descripcion: str = Field(min_length=1)
    producto: str = Field(min_length=1, max_length=180)
    dosis: str = Field(min_length=1, max_length=120)
    responsable: str = Field(min_length=1, max_length=120)
    fecha: datetime
    observaciones: str | None = None


class EventoSanitarioCreate(EventoSanitarioBase):
    pass


class EventoSanitarioUpdate(BaseModel):
    tipo_evento: TipoEventoSanitario | None = None
    descripcion: str | None = Field(default=None, min_length=1)
    producto: str | None = Field(default=None, min_length=1, max_length=180)
    dosis: str | None = Field(default=None, min_length=1, max_length=120)
    responsable: str | None = Field(default=None, min_length=1, max_length=120)
    fecha: datetime | None = None
    observaciones: str | None = None


class EventoSanitarioOut(EventoSanitarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime

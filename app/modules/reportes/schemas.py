from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReporteBase(BaseModel):
    tipo: str = Field(min_length=1, max_length=80)
    fecha_inicio: datetime
    fecha_fin: datetime
    formato: str = Field(min_length=1, max_length=20)
    url_archivo: str | None = None
    generado_por: str | None = Field(default=None, min_length=36, max_length=36)


class ReporteGenerarRequest(BaseModel):
    tipo: str = Field(min_length=1, max_length=80)
    fecha_inicio: datetime
    fecha_fin: datetime
    formato: str = Field(min_length=1, max_length=20)
    generado_por: str | None = Field(default=None, min_length=36, max_length=36)


class ReporteOut(ReporteBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime

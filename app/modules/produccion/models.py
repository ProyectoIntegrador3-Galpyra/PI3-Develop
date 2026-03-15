from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel


class ProduccionHuevo(BaseModel):
    __tablename__ = "produccion_huevos"

    galpon_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("galpones.id"),
        nullable=False,
        index=True,
    )
    lote_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("lotes_aves.id"),
        nullable=True,
        index=True,
    )
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    huevos_rotos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    galpon = relationship("Galpon", back_populates="producciones")
    lote = relationship("LoteAve", back_populates="producciones")

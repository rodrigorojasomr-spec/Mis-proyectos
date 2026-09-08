"""Modelo ORM de los comunicados publicados por la administración."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.nucleo.base_datos import Base


class Comunicado(Base):
    """Aviso o comunicado publicado por un administrador, visible para todos los
    residentes (ej. mantenimiento programado, reuniones, normas de convivencia)."""

    __tablename__ = "comunicados"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    destacado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

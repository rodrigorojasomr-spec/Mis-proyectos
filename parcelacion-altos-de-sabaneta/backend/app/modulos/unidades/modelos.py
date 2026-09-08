"""Modelo ORM de las unidades (casas/lotes) de la parcelación."""

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.nucleo.base_datos import Base


class Unidad(Base):
    """Representa una unidad habitacional de la parcelación (ej. una casa o lote),
    a la que se asocian las cuotas de mantenimiento. Puede tener o no un residente
    asignado (por ejemplo, un lote sin construir todavía)."""

    __tablename__ = "unidades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    residente_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    creado_en: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

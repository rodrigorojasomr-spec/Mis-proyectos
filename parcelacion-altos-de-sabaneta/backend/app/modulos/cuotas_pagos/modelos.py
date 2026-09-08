"""Modelos ORM de cuotas de mantenimiento y sus pagos asociados."""

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.nucleo.base_datos import Base


class EstadoCuota(str, enum.Enum):
    """Estado de una cuota según lo pagado hasta el momento."""

    PENDIENTE = "pendiente"
    PARCIAL = "parcial"
    PAGADA = "pagada"


class Cuota(Base):
    """Cuota de mantenimiento (u otro concepto) que debe pagar una unidad."""

    __tablename__ = "cuotas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    unidad_id: Mapped[int] = mapped_column(ForeignKey("unidades.id", ondelete="CASCADE"), nullable=False)
    concepto: Mapped[str] = mapped_column(String(150), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(nullable=False)
    estado: Mapped[EstadoCuota] = mapped_column(
        Enum(EstadoCuota, name="estado_cuota"), default=EstadoCuota.PENDIENTE, nullable=False
    )
    creado_en: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    pagos: Mapped[list["Pago"]] = relationship(back_populates="cuota", cascade="all, delete-orphan")

    @property
    def saldo_pendiente(self) -> Decimal:
        """Monto que aún falta pagar: el total de la cuota menos la suma de los pagos registrados."""
        total_pagado = sum((pago.monto_pagado for pago in self.pagos), Decimal("0"))
        return self.monto - total_pagado


class Pago(Base):
    """Abono (total o parcial) registrado contra una cuota."""

    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cuota_id: Mapped[int] = mapped_column(ForeignKey("cuotas.id", ondelete="CASCADE"), nullable=False)
    monto_pagado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    metodo_pago: Mapped[str] = mapped_column(String(50), nullable=False)
    registrado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    creado_en: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cuota: Mapped["Cuota"] = relationship(back_populates="pagos")

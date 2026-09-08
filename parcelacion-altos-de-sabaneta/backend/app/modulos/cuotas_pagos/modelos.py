"""Modelos ORM de cuotas de mantenimiento y sus pagos asociados."""

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.nucleo.base_datos import Base

# El pago de una cuota debe hacerse antes de su fecha de vencimiento (política de
# la parcelación: dentro de los primeros 5 días del mes). Cada día de atraso
# después de esa fecha suma este recargo fijo al saldo pendiente.
RECARGO_POR_DIA_MORA = Decimal("1000")


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
    def dias_mora(self) -> int:
        """Días transcurridos desde el vencimiento sin haberse pagado por completo.

        Mientras la cuota siga sin pagarse, la mora se cuenta hasta hoy (crece
        día a día). Una vez pagada, queda fija en la fecha del pago que la
        completó, para que el recargo no siga aumentando después de saldada.
        """
        if self.estado == EstadoCuota.PAGADA:
            if not self.pagos:
                return 0
            fecha_referencia = max(pago.creado_en for pago in self.pagos).date()
        else:
            fecha_referencia = date.today()

        return max(0, (fecha_referencia - self.fecha_vencimiento).days)

    @property
    def recargo_por_mora(self) -> Decimal:
        """Recargo acumulado: $1.000 por cada día de atraso sobre la fecha de vencimiento."""
        return Decimal(self.dias_mora) * RECARGO_POR_DIA_MORA

    @property
    def monto_con_recargo(self) -> Decimal:
        """Monto total a pagar incluyendo el recargo por mora, si aplica."""
        return self.monto + self.recargo_por_mora

    @property
    def saldo_pendiente(self) -> Decimal:
        """Monto que aún falta pagar: la cuota más su recargo por mora, menos lo ya pagado."""
        total_pagado = sum((pago.monto_pagado for pago in self.pagos), Decimal("0"))
        return self.monto_con_recargo - total_pagado


class Pago(Base):
    """Abono (total o parcial) registrado contra una cuota."""

    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cuota_id: Mapped[int] = mapped_column(ForeignKey("cuotas.id", ondelete="CASCADE"), nullable=False)
    monto_pagado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    metodo_pago: Mapped[str] = mapped_column(String(50), nullable=False)
    registrado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cuota: Mapped["Cuota"] = relationship(back_populates="pagos")

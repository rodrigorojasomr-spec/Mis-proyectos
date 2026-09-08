"""Esquemas Pydantic del módulo de reportes. Son de solo lectura: no representan
tablas propias, sino agregaciones calculadas sobre unidades, cuotas y pagos."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ResumenReporte(BaseModel):
    """Panorama financiero general de la parcelación."""

    total_unidades: int
    total_cuotas_emitidas: int
    monto_total_facturado: Decimal
    monto_total_recaudado: Decimal
    monto_total_pendiente: Decimal
    cuotas_pendientes: int
    cuotas_parciales: int
    cuotas_pagadas: int
    cuotas_vencidas: int


class CarteraUnidad(BaseModel):
    """Estado de cuenta de una unidad: lo facturado, lo recaudado y el saldo."""

    unidad_id: int
    codigo_unidad: str
    residente: str | None
    monto_facturado: Decimal
    monto_recaudado: Decimal
    saldo_pendiente: Decimal


class CuotaVencida(BaseModel):
    """Una cuota no pagada cuya fecha de vencimiento ya pasó."""

    cuota_id: int
    unidad_id: int
    codigo_unidad: str
    residente: str | None
    concepto: str
    monto: Decimal
    fecha_vencimiento: date
    dias_vencida: int
    saldo_pendiente: Decimal

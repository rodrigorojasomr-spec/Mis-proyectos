"""Esquemas Pydantic del módulo de cuotas y pagos."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.modulos.cuotas_pagos.modelos import EstadoCuota

METODOS_PAGO_VALIDOS = {"efectivo", "transferencia", "tarjeta", "consignacion"}


class CuotaCrear(BaseModel):
    """Datos para generar una cuota de mantenimiento sobre una unidad."""

    unidad_id: int
    concepto: str = Field(min_length=3, max_length=150)
    monto: Decimal = Field(gt=0, decimal_places=2)
    fecha_vencimiento: date

    @field_validator("concepto")
    @classmethod
    def limpiar_concepto(cls, valor: str) -> str:
        return valor.strip()


class PagoCrear(BaseModel):
    """Datos para registrar un abono sobre una cuota existente."""

    monto_pagado: Decimal = Field(gt=0, decimal_places=2)
    metodo_pago: str

    @field_validator("metodo_pago")
    @classmethod
    def validar_metodo_pago(cls, valor: str) -> str:
        valor_normalizado = valor.strip().lower()
        if valor_normalizado not in METODOS_PAGO_VALIDOS:
            raise ValueError(
                f"Método de pago inválido. Opciones válidas: {', '.join(sorted(METODOS_PAGO_VALIDOS))}"
            )
        return valor_normalizado


class PagoRespuesta(BaseModel):
    id: int
    cuota_id: int
    monto_pagado: Decimal
    metodo_pago: str
    registrado_por_id: int
    creado_en: datetime

    model_config = {"from_attributes": True}


class CuotaRespuesta(BaseModel):
    id: int
    unidad_id: int
    concepto: str
    monto: Decimal
    fecha_vencimiento: date
    estado: EstadoCuota
    dias_mora: int
    recargo_por_mora: Decimal
    monto_con_recargo: Decimal
    saldo_pendiente: Decimal

    model_config = {"from_attributes": True}


class CuotaConPagos(CuotaRespuesta):
    pagos: list[PagoRespuesta] = []

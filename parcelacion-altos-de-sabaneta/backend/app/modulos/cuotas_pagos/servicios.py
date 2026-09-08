"""Lógica de negocio del módulo de cuotas y pagos."""

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.modulos.autenticacion.modelos import Usuario
from app.modulos.cuotas_pagos.esquemas import CuotaCrear, PagoCrear
from app.modulos.cuotas_pagos.modelos import Cuota, EstadoCuota, Pago
from app.modulos.unidades.servicios import obtener_unidad_o_404, verificar_pertenencia_unidad


def crear_cuota(sesion: Session, datos: CuotaCrear) -> Cuota:
    """Crea una cuota para una unidad existente."""
    obtener_unidad_o_404(sesion, datos.unidad_id)

    nueva_cuota = Cuota(
        unidad_id=datos.unidad_id,
        concepto=datos.concepto,
        monto=datos.monto,
        fecha_vencimiento=datos.fecha_vencimiento,
    )
    sesion.add(nueva_cuota)
    sesion.commit()
    sesion.refresh(nueva_cuota)
    return nueva_cuota


def obtener_cuota_o_404(sesion: Session, cuota_id: int) -> Cuota:
    cuota = (
        sesion.query(Cuota)
        .options(joinedload(Cuota.pagos))
        .filter(Cuota.id == cuota_id)
        .first()
    )
    if cuota is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuota no encontrada")
    return cuota


def verificar_acceso_cuota(sesion: Session, cuota: Cuota, usuario: Usuario) -> None:
    """Un residente solo puede ver/pagar cuotas de su propia unidad."""
    unidad = obtener_unidad_o_404(sesion, cuota.unidad_id)
    verificar_pertenencia_unidad(unidad, usuario)


def listar_cuotas_por_unidad(sesion: Session, unidad_id: int) -> list[Cuota]:
    obtener_unidad_o_404(sesion, unidad_id)
    return (
        sesion.query(Cuota)
        .options(joinedload(Cuota.pagos))
        .filter(Cuota.unidad_id == unidad_id)
        .order_by(Cuota.fecha_vencimiento.desc())
        .all()
    )


def registrar_pago(sesion: Session, cuota_id: int, datos: PagoCrear, usuario_actual: Usuario) -> Pago:
    """Registra un abono sobre una cuota, validando que no exceda el saldo pendiente
    y actualizando el estado de la cuota (pendiente / parcial / pagada)."""
    cuota = obtener_cuota_o_404(sesion, cuota_id)
    verificar_acceso_cuota(sesion, cuota, usuario_actual)

    if cuota.estado == EstadoCuota.PAGADA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta cuota ya se encuentra pagada en su totalidad",
        )

    if datos.monto_pagado > cuota.saldo_pendiente:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"El monto pagado (${datos.monto_pagado}) supera el saldo pendiente "
                f"(${cuota.saldo_pendiente})"
            ),
        )

    nuevo_pago = Pago(
        monto_pagado=datos.monto_pagado,
        metodo_pago=datos.metodo_pago,
        registrado_por_id=usuario_actual.id,
    )
    # Se asocia mediante la relación (no el id) para que cuota.pagos quede
    # actualizada en memoria de inmediato y el cálculo de saldo sea correcto.
    cuota.pagos.append(nuevo_pago)
    sesion.flush()

    saldo_restante = cuota.saldo_pendiente
    if saldo_restante <= Decimal("0"):
        cuota.estado = EstadoCuota.PAGADA
    else:
        cuota.estado = EstadoCuota.PARCIAL

    sesion.commit()
    sesion.refresh(nuevo_pago)
    return nuevo_pago

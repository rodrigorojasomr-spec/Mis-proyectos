"""Lógica de agregación del módulo de reportes.

No hay modelos propios: se calculan cifras a partir de unidades, cuotas y pagos
ya existentes. Los volúmenes esperados en una parcelación (decenas/cientos de
unidades) permiten cargar las cuotas con sus pagos y calcular todo en Python
reutilizando `Cuota.saldo_pendiente`, en vez de duplicar esa lógica en SQL.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.modulos.autenticacion.modelos import Usuario
from app.modulos.cuotas_pagos.modelos import Cuota, EstadoCuota
from app.modulos.reportes.esquemas import CarteraUnidad, CuotaVencida, ResumenReporte
from app.modulos.unidades.modelos import Unidad


def _cargar_cuotas_con_pagos(sesion: Session) -> list[Cuota]:
    return sesion.query(Cuota).options(joinedload(Cuota.pagos)).all()


def _mapa_nombres_residentes(sesion: Session) -> dict[int, str]:
    return {usuario.id: usuario.nombre_completo for usuario in sesion.query(Usuario).all()}


def generar_resumen(sesion: Session) -> ResumenReporte:
    """Calcula el panorama financiero general de la parcelación."""
    cuotas = _cargar_cuotas_con_pagos(sesion)
    hoy = date.today()

    monto_facturado = sum((cuota.monto for cuota in cuotas), Decimal("0"))
    monto_pendiente = sum((cuota.saldo_pendiente for cuota in cuotas), Decimal("0"))
    monto_recaudado = monto_facturado - monto_pendiente

    return ResumenReporte(
        total_unidades=sesion.query(Unidad).count(),
        total_cuotas_emitidas=len(cuotas),
        monto_total_facturado=monto_facturado,
        monto_total_recaudado=monto_recaudado,
        monto_total_pendiente=monto_pendiente,
        cuotas_pendientes=sum(1 for c in cuotas if c.estado == EstadoCuota.PENDIENTE),
        cuotas_parciales=sum(1 for c in cuotas if c.estado == EstadoCuota.PARCIAL),
        cuotas_pagadas=sum(1 for c in cuotas if c.estado == EstadoCuota.PAGADA),
        cuotas_vencidas=sum(
            1 for c in cuotas if c.estado != EstadoCuota.PAGADA and c.fecha_vencimiento < hoy
        ),
    )


def generar_cartera_por_unidad(sesion: Session) -> list[CarteraUnidad]:
    """Estado de cuenta (facturado / recaudado / saldo) de cada unidad."""
    unidades = sesion.query(Unidad).order_by(Unidad.codigo).all()
    cuotas = _cargar_cuotas_con_pagos(sesion)
    nombres_residentes = _mapa_nombres_residentes(sesion)

    cuotas_por_unidad: dict[int, list[Cuota]] = {}
    for cuota in cuotas:
        cuotas_por_unidad.setdefault(cuota.unidad_id, []).append(cuota)

    resultado = []
    for unidad in unidades:
        cuotas_unidad = cuotas_por_unidad.get(unidad.id, [])
        facturado = sum((cuota.monto for cuota in cuotas_unidad), Decimal("0"))
        pendiente = sum((cuota.saldo_pendiente for cuota in cuotas_unidad), Decimal("0"))

        resultado.append(
            CarteraUnidad(
                unidad_id=unidad.id,
                codigo_unidad=unidad.codigo,
                residente=nombres_residentes.get(unidad.residente_id) if unidad.residente_id else None,
                monto_facturado=facturado,
                monto_recaudado=facturado - pendiente,
                saldo_pendiente=pendiente,
            )
        )

    return resultado


def generar_cuotas_vencidas(sesion: Session) -> list[CuotaVencida]:
    """Lista las cuotas no pagadas cuya fecha de vencimiento ya pasó,
    ordenadas de la más antigua a la más reciente."""
    hoy = date.today()
    cuotas = _cargar_cuotas_con_pagos(sesion)
    unidades_por_id = {unidad.id: unidad for unidad in sesion.query(Unidad).all()}
    nombres_residentes = _mapa_nombres_residentes(sesion)

    vencidas = [
        cuota for cuota in cuotas if cuota.estado != EstadoCuota.PAGADA and cuota.fecha_vencimiento < hoy
    ]
    vencidas.sort(key=lambda cuota: cuota.fecha_vencimiento)

    resultado = []
    for cuota in vencidas:
        unidad = unidades_por_id[cuota.unidad_id]
        resultado.append(
            CuotaVencida(
                cuota_id=cuota.id,
                unidad_id=unidad.id,
                codigo_unidad=unidad.codigo,
                residente=nombres_residentes.get(unidad.residente_id) if unidad.residente_id else None,
                concepto=cuota.concepto,
                monto=cuota.monto,
                fecha_vencimiento=cuota.fecha_vencimiento,
                dias_vencida=(hoy - cuota.fecha_vencimiento).days,
                saldo_pendiente=cuota.saldo_pendiente,
            )
        )

    return resultado

"""Endpoints HTTP del módulo de cuotas y pagos."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.modulos.autenticacion.modelos import Usuario
from app.modulos.cuotas_pagos.esquemas import CuotaConPagos, CuotaCrear, PagoCrear, PagoRespuesta
from app.modulos.cuotas_pagos.modelos import Cuota, Pago
from app.modulos.cuotas_pagos.servicios import (
    crear_cuota,
    listar_cuotas_por_unidad,
    obtener_cuota_o_404,
    registrar_pago,
    verificar_acceso_cuota,
)
from app.modulos.unidades.servicios import obtener_unidad_o_404, verificar_pertenencia_unidad
from app.nucleo.base_datos import obtener_sesion_bd
from app.nucleo.dependencias import obtener_usuario_actual, requerir_rol

enrutador = APIRouter(prefix="/api/cuotas", tags=["Cuotas y pagos"])


@enrutador.post("", response_model=CuotaConPagos, status_code=status.HTTP_201_CREATED)
def crear(
    datos: CuotaCrear,
    sesion: Session = Depends(obtener_sesion_bd),
    _administrador: Usuario = Depends(requerir_rol("administrador")),
) -> Cuota:
    """Genera una nueva cuota para una unidad. Solo el administrador puede hacerlo."""
    return crear_cuota(sesion, datos)


@enrutador.get("/unidad/{unidad_id}", response_model=list[CuotaConPagos])
def listar_por_unidad(
    unidad_id: int,
    sesion: Session = Depends(obtener_sesion_bd),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> list[Cuota]:
    """Lista las cuotas de una unidad. El residente solo puede ver las de su propia unidad."""
    unidad = obtener_unidad_o_404(sesion, unidad_id)
    verificar_pertenencia_unidad(unidad, usuario_actual)
    return listar_cuotas_por_unidad(sesion, unidad_id)


@enrutador.get("/{cuota_id}", response_model=CuotaConPagos)
def obtener(
    cuota_id: int,
    sesion: Session = Depends(obtener_sesion_bd),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> Cuota:
    """Obtiene el detalle de una cuota junto con sus pagos."""
    cuota = obtener_cuota_o_404(sesion, cuota_id)
    verificar_acceso_cuota(sesion, cuota, usuario_actual)
    return cuota


@enrutador.post("/{cuota_id}/pagos", response_model=PagoRespuesta, status_code=status.HTTP_201_CREATED)
def pagar(
    cuota_id: int,
    datos: PagoCrear,
    sesion: Session = Depends(obtener_sesion_bd),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> Pago:
    """Registra un abono sobre una cuota. El residente solo puede pagar cuotas de su unidad;
    el administrador puede registrar pagos de cualquier unidad (ej. pagos en efectivo en oficina)."""
    return registrar_pago(sesion, cuota_id, datos, usuario_actual)

"""Endpoints HTTP del módulo de reportes. Toda la información es financiera
y de gestión, por lo que se restringe exclusivamente al administrador."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.modulos.autenticacion.modelos import Usuario
from app.modulos.reportes.esquemas import CarteraUnidad, CuotaVencida, ResumenReporte
from app.modulos.reportes.servicios import (
    generar_cartera_por_unidad,
    generar_cuotas_vencidas,
    generar_resumen,
)
from app.nucleo.base_datos import obtener_sesion_bd
from app.nucleo.dependencias import requerir_rol

enrutador = APIRouter(prefix="/api/reportes", tags=["Reportes"])


@enrutador.get("/resumen", response_model=ResumenReporte)
def resumen(
    sesion: Session = Depends(obtener_sesion_bd),
    _administrador: Usuario = Depends(requerir_rol("administrador")),
) -> ResumenReporte:
    """Panorama financiero general: facturado, recaudado, pendiente y conteo por estado."""
    return generar_resumen(sesion)


@enrutador.get("/cartera", response_model=list[CarteraUnidad])
def cartera(
    sesion: Session = Depends(obtener_sesion_bd),
    _administrador: Usuario = Depends(requerir_rol("administrador")),
) -> list[CarteraUnidad]:
    """Estado de cuenta de cada unidad."""
    return generar_cartera_por_unidad(sesion)


@enrutador.get("/cuotas-vencidas", response_model=list[CuotaVencida])
def cuotas_vencidas(
    sesion: Session = Depends(obtener_sesion_bd),
    _administrador: Usuario = Depends(requerir_rol("administrador")),
) -> list[CuotaVencida]:
    """Cuotas no pagadas cuya fecha de vencimiento ya pasó."""
    return generar_cuotas_vencidas(sesion)

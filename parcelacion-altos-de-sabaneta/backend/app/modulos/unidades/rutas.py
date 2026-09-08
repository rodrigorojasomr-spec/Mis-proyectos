"""Endpoints HTTP del módulo de unidades."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.modulos.autenticacion.modelos import Usuario
from app.modulos.unidades.esquemas import UnidadAsignarResidente, UnidadCrear, UnidadRespuesta
from app.modulos.unidades.modelos import Unidad
from app.modulos.unidades.servicios import (
    asignar_residente,
    crear_unidad,
    listar_unidades,
    obtener_unidad_del_residente,
)
from app.nucleo.base_datos import obtener_sesion_bd
from app.nucleo.dependencias import obtener_usuario_actual, requerir_rol

enrutador = APIRouter(prefix="/api/unidades", tags=["Unidades"])


@enrutador.post("", response_model=UnidadRespuesta, status_code=status.HTTP_201_CREATED)
def crear(
    datos: UnidadCrear,
    sesion: Session = Depends(obtener_sesion_bd),
    _administrador: Usuario = Depends(requerir_rol("administrador")),
) -> Unidad:
    """Registra una nueva unidad. Solo el administrador puede hacerlo."""
    return crear_unidad(sesion, datos)


@enrutador.get("", response_model=list[UnidadRespuesta])
def listar(
    sesion: Session = Depends(obtener_sesion_bd),
    _administrador: Usuario = Depends(requerir_rol("administrador")),
) -> list[Unidad]:
    """Lista todas las unidades de la parcelación. Solo el administrador."""
    return listar_unidades(sesion)


@enrutador.get("/mia", response_model=UnidadRespuesta | None)
def mi_unidad(
    sesion: Session = Depends(obtener_sesion_bd),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> Unidad | None:
    """Devuelve la unidad asignada al residente autenticado (o null si aún no tiene una)."""
    return obtener_unidad_del_residente(sesion, usuario_actual.id)


@enrutador.patch("/{unidad_id}/residente", response_model=UnidadRespuesta)
def cambiar_residente(
    unidad_id: int,
    datos: UnidadAsignarResidente,
    sesion: Session = Depends(obtener_sesion_bd),
    _administrador: Usuario = Depends(requerir_rol("administrador")),
) -> Unidad:
    """Asigna o retira el residente responsable de una unidad. Solo el administrador."""
    return asignar_residente(sesion, unidad_id, datos.residente_id)

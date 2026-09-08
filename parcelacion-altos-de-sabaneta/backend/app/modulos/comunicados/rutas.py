"""Endpoints HTTP del módulo de comunicados."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.modulos.autenticacion.modelos import Usuario
from app.modulos.comunicados.esquemas import ComunicadoActualizar, ComunicadoCrear, ComunicadoRespuesta
from app.modulos.comunicados.modelos import Comunicado
from app.modulos.comunicados.servicios import (
    actualizar_comunicado,
    crear_comunicado,
    eliminar_comunicado,
    listar_comunicados,
    obtener_comunicado_o_404,
)
from app.nucleo.base_datos import obtener_sesion_bd
from app.nucleo.dependencias import obtener_usuario_actual, requerir_rol

enrutador = APIRouter(prefix="/api/comunicados", tags=["Comunicados"])


@enrutador.post("", response_model=ComunicadoRespuesta, status_code=status.HTTP_201_CREATED)
def crear(
    datos: ComunicadoCrear,
    sesion: Session = Depends(obtener_sesion_bd),
    administrador: Usuario = Depends(requerir_rol("administrador")),
) -> Comunicado:
    """Publica un nuevo comunicado. Solo el administrador puede hacerlo."""
    return crear_comunicado(sesion, datos, administrador.id)


@enrutador.get("", response_model=list[ComunicadoRespuesta])
def listar(
    sesion: Session = Depends(obtener_sesion_bd),
    _usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> list[Comunicado]:
    """Lista todos los comunicados. Visible para cualquier usuario autenticado."""
    return listar_comunicados(sesion)


@enrutador.get("/{comunicado_id}", response_model=ComunicadoRespuesta)
def obtener(
    comunicado_id: int,
    sesion: Session = Depends(obtener_sesion_bd),
    _usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> Comunicado:
    """Obtiene el detalle de un comunicado."""
    return obtener_comunicado_o_404(sesion, comunicado_id)


@enrutador.patch("/{comunicado_id}", response_model=ComunicadoRespuesta)
def actualizar(
    comunicado_id: int,
    datos: ComunicadoActualizar,
    sesion: Session = Depends(obtener_sesion_bd),
    _administrador: Usuario = Depends(requerir_rol("administrador")),
) -> Comunicado:
    """Edita un comunicado existente. Solo el administrador puede hacerlo."""
    return actualizar_comunicado(sesion, comunicado_id, datos)


@enrutador.delete("/{comunicado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    comunicado_id: int,
    sesion: Session = Depends(obtener_sesion_bd),
    _administrador: Usuario = Depends(requerir_rol("administrador")),
) -> None:
    """Elimina un comunicado. Solo el administrador puede hacerlo."""
    eliminar_comunicado(sesion, comunicado_id)

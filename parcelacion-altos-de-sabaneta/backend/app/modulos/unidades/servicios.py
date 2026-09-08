"""Lógica de negocio del módulo de unidades."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modulos.autenticacion.modelos import Usuario
from app.modulos.unidades.esquemas import UnidadCrear
from app.modulos.unidades.modelos import Unidad


def validar_residente_existe(sesion: Session, residente_id: int | None) -> None:
    """Si se indica un residente, valida que exista antes de asociarlo a una unidad."""
    if residente_id is None:
        return
    residente = sesion.get(Usuario, residente_id)
    if residente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El residente indicado no existe",
        )


def crear_unidad(sesion: Session, datos: UnidadCrear) -> Unidad:
    """Crea una unidad validando que el código no esté repetido."""
    codigo_existente = sesion.query(Unidad).filter(Unidad.codigo == datos.codigo).first()
    if codigo_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una unidad registrada con ese código",
        )

    validar_residente_existe(sesion, datos.residente_id)

    nueva_unidad = Unidad(codigo=datos.codigo, residente_id=datos.residente_id)
    sesion.add(nueva_unidad)
    sesion.commit()
    sesion.refresh(nueva_unidad)
    return nueva_unidad


def obtener_unidad_o_404(sesion: Session, unidad_id: int) -> Unidad:
    unidad = sesion.get(Unidad, unidad_id)
    if unidad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidad no encontrada")
    return unidad


def listar_unidades(sesion: Session) -> list[Unidad]:
    return sesion.query(Unidad).order_by(Unidad.codigo).all()


def obtener_unidad_del_residente(sesion: Session, residente_id: int) -> Unidad | None:
    """Devuelve la unidad asignada al residente autenticado, o None si no tiene ninguna."""
    return sesion.query(Unidad).filter(Unidad.residente_id == residente_id).first()


def asignar_residente(sesion: Session, unidad_id: int, residente_id: int | None) -> Unidad:
    unidad = obtener_unidad_o_404(sesion, unidad_id)
    validar_residente_existe(sesion, residente_id)
    unidad.residente_id = residente_id
    sesion.commit()
    sesion.refresh(unidad)
    return unidad


def verificar_pertenencia_unidad(unidad: Unidad, usuario: Usuario) -> None:
    """Verifica que la unidad pertenezca al residente autenticado.
    Los administradores tienen acceso a todas las unidades."""
    if usuario.rol == "administrador":
        return
    if unidad.residente_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a la información de esta unidad",
        )

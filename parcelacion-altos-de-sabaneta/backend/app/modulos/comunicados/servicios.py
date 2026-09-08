"""Lógica de negocio del módulo de comunicados."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modulos.comunicados.esquemas import ComunicadoActualizar, ComunicadoCrear
from app.modulos.comunicados.modelos import Comunicado


def crear_comunicado(sesion: Session, datos: ComunicadoCrear, autor_id: int) -> Comunicado:
    """Publica un nuevo comunicado a nombre del administrador autenticado."""
    nuevo_comunicado = Comunicado(
        titulo=datos.titulo,
        contenido=datos.contenido,
        destacado=datos.destacado,
        autor_id=autor_id,
    )
    sesion.add(nuevo_comunicado)
    sesion.commit()
    sesion.refresh(nuevo_comunicado)
    return nuevo_comunicado


def listar_comunicados(sesion: Session) -> list[Comunicado]:
    """Lista los comunicados con los destacados primero y los más recientes arriba."""
    return (
        sesion.query(Comunicado)
        .order_by(Comunicado.destacado.desc(), Comunicado.creado_en.desc())
        .all()
    )


def obtener_comunicado_o_404(sesion: Session, comunicado_id: int) -> Comunicado:
    comunicado = sesion.get(Comunicado, comunicado_id)
    if comunicado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunicado no encontrado")
    return comunicado


def actualizar_comunicado(sesion: Session, comunicado_id: int, datos: ComunicadoActualizar) -> Comunicado:
    comunicado = obtener_comunicado_o_404(sesion, comunicado_id)

    datos_a_actualizar = datos.model_dump(exclude_unset=True)
    for campo, valor in datos_a_actualizar.items():
        setattr(comunicado, campo, valor)

    sesion.commit()
    sesion.refresh(comunicado)
    return comunicado


def eliminar_comunicado(sesion: Session, comunicado_id: int) -> None:
    comunicado = obtener_comunicado_o_404(sesion, comunicado_id)
    sesion.delete(comunicado)
    sesion.commit()

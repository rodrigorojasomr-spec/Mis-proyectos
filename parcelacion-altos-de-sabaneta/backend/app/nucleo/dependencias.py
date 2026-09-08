"""Dependencias reutilizables de FastAPI para proteger endpoints por autenticación y rol."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.modulos.autenticacion.modelos import Usuario
from app.nucleo.base_datos import obtener_sesion_bd
from app.nucleo.seguridad import decodificar_token_acceso

# Indica a FastAPI dónde está el endpoint de login (para la documentación /docs)
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/autenticacion/login")


def obtener_usuario_actual(
    token: str = Depends(esquema_oauth2),
    sesion: Session = Depends(obtener_sesion_bd),
) -> Usuario:
    """Valida el token JWT recibido y devuelve el usuario autenticado.
    Lanza 401 si el token es inválido, expiró o el usuario ya no existe."""
    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    contenido_token = decodificar_token_acceso(token)
    if contenido_token is None:
        raise excepcion_credenciales

    id_usuario = contenido_token.get("sub")
    if id_usuario is None:
        raise excepcion_credenciales

    usuario = sesion.get(Usuario, int(id_usuario))
    if usuario is None or not usuario.esta_activo:
        raise excepcion_credenciales

    return usuario


def requerir_rol(*roles_permitidos: str):
    """Fábrica de dependencias: exige que el usuario autenticado tenga uno de los roles indicados.
    Uso: Depends(requerir_rol("administrador"))"""

    def verificador(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para realizar esta acción",
            )
        return usuario

    return verificador

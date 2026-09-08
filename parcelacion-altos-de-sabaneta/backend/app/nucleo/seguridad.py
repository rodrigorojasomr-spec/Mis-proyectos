"""Funciones de seguridad: hash de contraseñas y manejo de tokens JWT."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.nucleo.configuracion import obtener_configuracion

configuracion = obtener_configuracion()

contexto_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")


def obtener_hash_contrasena(contrasena_plana: str) -> str:
    """Genera el hash seguro (bcrypt) de una contraseña en texto plano.
    Nunca se debe guardar ni comparar la contraseña en texto plano."""
    return contexto_hash.hash(contrasena_plana)


def verificar_contrasena(contrasena_plana: str, contrasena_hasheada: str) -> bool:
    """Compara una contraseña en texto plano contra su hash almacenado."""
    return contexto_hash.verify(contrasena_plana, contrasena_hasheada)


def crear_token_acceso(datos: dict[str, Any]) -> str:
    """Crea un JWT firmado con expiración, usado como token de sesión."""
    datos_a_codificar = datos.copy()
    expiracion = datetime.now(UTC) + timedelta(minutes=configuracion.minutos_expiracion_token)
    datos_a_codificar.update({"exp": expiracion})
    return jwt.encode(
        datos_a_codificar,
        configuracion.clave_secreta_jwt,
        algorithm=configuracion.algoritmo_jwt,
    )


def decodificar_token_acceso(token: str) -> dict[str, Any] | None:
    """Decodifica y valida un JWT. Devuelve None si el token es inválido o expiró."""
    try:
        return jwt.decode(
            token,
            configuracion.clave_secreta_jwt,
            algorithms=[configuracion.algoritmo_jwt],
        )
    except JWTError:
        return None

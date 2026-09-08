"""Esquemas Pydantic: validan la forma y el contenido de los datos que entran y salen de la API."""

import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.modulos.autenticacion.modelos import RolUsuario

PATRON_CONTRASENA_SEGURA = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


class UsuarioRegistro(BaseModel):
    """Datos requeridos para registrar un nuevo usuario en la parcelación."""

    nombre_completo: str = Field(min_length=3, max_length=150)
    correo_electronico: EmailStr
    contrasena: str = Field(min_length=8, max_length=72)
    rol: RolUsuario = RolUsuario.RESIDENTE

    @field_validator("contrasena")
    @classmethod
    def validar_fortaleza_contrasena(cls, valor: str) -> str:
        """Exige mínimo 8 caracteres con al menos una letra y un número,
        para evitar contraseñas triviales (seguridad mínima obligatoria)."""
        if not PATRON_CONTRASENA_SEGURA.match(valor):
            raise ValueError("La contraseña debe tener mínimo 8 caracteres, con letras y números")
        return valor

    @field_validator("nombre_completo")
    @classmethod
    def limpiar_nombre(cls, valor: str) -> str:
        return valor.strip()


class UsuarioInicioSesion(BaseModel):
    """Credenciales para iniciar sesión."""

    correo_electronico: EmailStr
    contrasena: str = Field(min_length=1, max_length=72)


class UsuarioRespuesta(BaseModel):
    """Representación pública del usuario, sin datos sensibles como la contraseña."""

    id: int
    nombre_completo: str
    correo_electronico: EmailStr
    rol: RolUsuario
    esta_activo: bool

    model_config = {"from_attributes": True}


class TokenAcceso(BaseModel):
    """Respuesta entregada tras un login exitoso."""

    token_acceso: str
    tipo_token: str = "bearer"
    usuario: UsuarioRespuesta

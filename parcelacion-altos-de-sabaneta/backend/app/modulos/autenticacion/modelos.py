"""Modelo ORM del usuario del sistema (administradores y residentes)."""

import enum

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.nucleo.base_datos import Base


class RolUsuario(str, enum.Enum):
    """Roles soportados dentro de la parcelación."""

    ADMINISTRADOR = "administrador"
    RESIDENTE = "residente"


class Usuario(Base):
    """Representa a una persona con acceso al sistema: un administrador
    de la parcelación o un residente propietario/arrendatario de una unidad."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    correo_electronico: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    contrasena_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario, name="rol_usuario"), default=RolUsuario.RESIDENTE, nullable=False
    )
    esta_activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    creado_en: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

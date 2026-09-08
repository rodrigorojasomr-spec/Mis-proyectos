"""Configuración de la conexión a la base de datos con SQLAlchemy."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.nucleo.configuracion import obtener_configuracion

configuracion = obtener_configuracion()

motor = create_engine(configuracion.url_base_datos, pool_pre_ping=True)

SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)


class Base(DeclarativeBase):
    """Clase base declarativa de la que heredan todos los modelos ORM."""


def obtener_sesion_bd() -> Generator[Session, None, None]:
    """Dependencia de FastAPI que entrega una sesión de base de datos por request
    y la cierra siempre al finalizar, incluso si ocurre un error."""
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()

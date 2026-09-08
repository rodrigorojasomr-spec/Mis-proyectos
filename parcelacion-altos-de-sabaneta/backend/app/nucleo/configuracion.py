"""Configuración centralizada de la aplicación, leída desde variables de entorno."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    # Conexión a la base de datos (Supabase Postgres o Postgres propio)
    url_base_datos: str = "postgresql://usuario:clave@localhost:5432/parcelacion_altos_sabaneta"

    # Parámetros de seguridad para tokens JWT
    clave_secreta_jwt: str = "cambiar-esta-clave-en-produccion"
    algoritmo_jwt: str = "HS256"
    minutos_expiracion_token: int = 60 * 8  # 8 horas de sesión

    # Orígenes permitidos para CORS (frontend Next.js)
    origenes_permitidos: list[str] = [
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve la configuración como singleton (cacheada) para evitar releer el .env."""
    return Configuracion()

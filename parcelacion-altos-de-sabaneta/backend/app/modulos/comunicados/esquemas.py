"""Esquemas Pydantic del módulo de comunicados."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ComunicadoCrear(BaseModel):
    """Datos para publicar un nuevo comunicado. Solo el administrador puede hacerlo."""

    titulo: str = Field(min_length=3, max_length=150)
    contenido: str = Field(min_length=1, max_length=5000)
    destacado: bool = False

    @field_validator("titulo", "contenido")
    @classmethod
    def limpiar_texto(cls, valor: str) -> str:
        return valor.strip()


class ComunicadoActualizar(BaseModel):
    """Datos para editar un comunicado existente. Todos los campos son opcionales."""

    titulo: str | None = Field(default=None, min_length=3, max_length=150)
    contenido: str | None = Field(default=None, min_length=1, max_length=5000)
    destacado: bool | None = None

    @field_validator("titulo", "contenido")
    @classmethod
    def limpiar_texto(cls, valor: str | None) -> str | None:
        return valor.strip() if valor is not None else None


class ComunicadoRespuesta(BaseModel):
    id: int
    titulo: str
    contenido: str
    destacado: bool
    autor_id: int
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}

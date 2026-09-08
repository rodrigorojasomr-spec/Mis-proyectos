"""Esquemas Pydantic del módulo de unidades."""

from pydantic import BaseModel, Field, field_validator


class UnidadCrear(BaseModel):
    """Datos para registrar una nueva unidad. Solo el administrador puede crearlas."""

    codigo: str = Field(min_length=1, max_length=50)
    residente_id: int | None = None

    @field_validator("codigo")
    @classmethod
    def limpiar_codigo(cls, valor: str) -> str:
        return valor.strip()


class UnidadAsignarResidente(BaseModel):
    """Permite asignar o quitar (null) el residente responsable de una unidad."""

    residente_id: int | None = None


class UnidadRespuesta(BaseModel):
    id: int
    codigo: str
    residente_id: int | None

    model_config = {"from_attributes": True}

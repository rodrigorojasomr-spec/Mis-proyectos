"""Endpoints HTTP del módulo de autenticación."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.modulos.autenticacion.esquemas import (
    TokenAcceso,
    UsuarioInicioSesion,
    UsuarioRegistro,
    UsuarioRespuesta,
)
from app.modulos.autenticacion.modelos import Usuario
from app.modulos.autenticacion.servicios import (
    autenticar_usuario,
    generar_token_para_usuario,
    registrar_usuario,
)
from app.nucleo.base_datos import obtener_sesion_bd
from app.nucleo.dependencias import obtener_usuario_actual

enrutador = APIRouter(prefix="/api/autenticacion", tags=["Autenticación"])


@enrutador.post("/registro", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registro(datos: UsuarioRegistro, sesion: Session = Depends(obtener_sesion_bd)) -> Usuario:
    """Registra un nuevo residente o administrador.
    La validación de formato y fortaleza de contraseña ocurre en el esquema Pydantic."""
    return registrar_usuario(sesion, datos)


@enrutador.post("/login", response_model=TokenAcceso)
def login(credenciales: UsuarioInicioSesion, sesion: Session = Depends(obtener_sesion_bd)) -> TokenAcceso:
    """Autentica al usuario y entrega un token JWT de acceso."""
    usuario = autenticar_usuario(sesion, credenciales)
    token = generar_token_para_usuario(usuario)
    return TokenAcceso(token_acceso=token, usuario=UsuarioRespuesta.model_validate(usuario))


@enrutador.get("/perfil", response_model=UsuarioRespuesta)
def perfil(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    """Devuelve los datos del usuario autenticado a partir de su token."""
    return usuario_actual

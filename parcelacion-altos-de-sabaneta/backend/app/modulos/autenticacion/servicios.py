"""Lógica de negocio del módulo de autenticación, separada de las rutas HTTP."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modulos.autenticacion.esquemas import UsuarioInicioSesion, UsuarioRegistro
from app.modulos.autenticacion.modelos import Usuario
from app.nucleo.seguridad import crear_token_acceso, obtener_hash_contrasena, verificar_contrasena


def registrar_usuario(sesion: Session, datos: UsuarioRegistro) -> Usuario:
    """Crea un nuevo usuario validando que el correo no esté ya registrado."""
    correo_normalizado = datos.correo_electronico.lower()

    usuario_existente = (
        sesion.query(Usuario).filter(Usuario.correo_electronico == correo_normalizado).first()
    )
    if usuario_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario registrado con este correo electrónico",
        )

    nuevo_usuario = Usuario(
        nombre_completo=datos.nombre_completo,
        correo_electronico=correo_normalizado,
        contrasena_hash=obtener_hash_contrasena(datos.contrasena),
        rol=datos.rol,
    )
    sesion.add(nuevo_usuario)
    sesion.commit()
    sesion.refresh(nuevo_usuario)
    return nuevo_usuario


def autenticar_usuario(sesion: Session, credenciales: UsuarioInicioSesion) -> Usuario:
    """Verifica correo y contraseña. Devuelve el usuario si son correctos."""
    correo_normalizado = credenciales.correo_electronico.lower()
    usuario = sesion.query(Usuario).filter(Usuario.correo_electronico == correo_normalizado).first()

    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Correo o contraseña incorrectos",
    )

    if usuario is None or not verificar_contrasena(credenciales.contrasena, usuario.contrasena_hash):
        raise credenciales_invalidas

    if not usuario.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta cuenta está desactivada. Contacta al administrador de la parcelación",
        )

    return usuario


def generar_token_para_usuario(usuario: Usuario) -> str:
    """Genera el JWT de sesión incluyendo el id y el rol del usuario."""
    return crear_token_acceso({"sub": str(usuario.id), "rol": usuario.rol.value})

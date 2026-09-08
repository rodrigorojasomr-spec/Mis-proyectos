"""Punto de entrada de la API de Parcelación Altos de Sabaneta."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modulos.autenticacion.rutas import enrutador as enrutador_autenticacion
from app.modulos.comunicados.rutas import enrutador as enrutador_comunicados
from app.modulos.cuotas_pagos.rutas import enrutador as enrutador_cuotas_pagos
from app.modulos.reportes.rutas import enrutador as enrutador_reportes
from app.modulos.unidades.rutas import enrutador as enrutador_unidades
from app.nucleo.base_datos import Base, motor
from app.nucleo.configuracion import obtener_configuracion

configuracion = obtener_configuracion()

# Crea las tablas si no existen (en producción se recomienda usar migraciones tipo Alembic)
Base.metadata.create_all(bind=motor)

aplicacion = FastAPI(
    title="API Parcelación Altos de Sabaneta",
    description="Sistema de administración de la parcelación: usuarios, unidades y cuotas.",
    version="0.1.0",
)

aplicacion.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cada módulo de negocio (autenticación, unidades, cuotas, etc.) expone su propio router.
aplicacion.include_router(enrutador_autenticacion)
aplicacion.include_router(enrutador_unidades)
aplicacion.include_router(enrutador_cuotas_pagos)
aplicacion.include_router(enrutador_comunicados)
aplicacion.include_router(enrutador_reportes)


@aplicacion.get("/api/salud", tags=["Salud"])
def verificar_salud() -> dict[str, str]:
    """Endpoint simple para confirmar que la API está en línea."""
    return {"estado": "ok"}

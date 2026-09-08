# Parcelación Altos de Sabaneta

Sistema de administración de condominios/parcelación. Este repositorio contiene
el arranque del proyecto con **arquitectura modular**: cada funcionalidad de
negocio (autenticación, unidades, cuotas, etc.) vive en su propio módulo tanto
en el backend como en el frontend.

## Estado actual

- ✅ Estructura base del proyecto (backend + frontend).
- ✅ Módulo de **autenticación**: registro, login y perfil, con roles
  `administrador` y `residente`.
- ✅ Módulo de **unidades**: registro de casas/lotes y asignación de residente
  (prerequisito mínimo para asociar cuotas a un inmueble).
- ✅ Módulo de **cuotas y pagos**: generación de cuotas de mantenimiento por
  unidad, registro de abonos (totales o parciales) con validación de saldo y
  cálculo automático de estado (`pendiente` / `parcial` / `pagada`).
- ✅ Módulo de **comunicados**: publicación de avisos por parte del
  administrador (con opción de destacarlos), visibles para todos los usuarios.
- ⏳ Próximos módulos: reportes (cartera, cuotas vencidas, etc.).

> Nota: esta parcelación no cuenta con zonas comunes de uso reservable
> (salón social, cancha, etc.), por lo que no se contempla un módulo de
> reservas.

## Stack técnico

| Capa       | Tecnología                          |
|------------|--------------------------------------|
| Frontend   | Next.js 14 (App Router) + TypeScript |
| Backend    | FastAPI (Python)                     |
| Base de datos | PostgreSQL / Supabase             |
| Autenticación | JWT + bcrypt                      |

## Estructura del proyecto

```
parcelacion-altos-de-sabaneta/
├── backend/
│   ├── app/
│   │   ├── main.py                  # Punto de entrada de la API
│   │   ├── nucleo/                  # Configuración, BD, seguridad, dependencias
│   │   └── modulos/
│   │       ├── autenticacion/       # Modelo, esquemas, servicios y rutas
│   │       ├── unidades/            # Casas/lotes y asignación de residente
│   │       ├── cuotas_pagos/        # Cuotas de mantenimiento y sus abonos
│   │       └── comunicados/         # Avisos publicados por la administración
│   ├── supabase/esquema.sql         # Esquema SQL de referencia
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── (auth)/iniciar-sesion/
    │   ├── (auth)/registro/
    │   └── panel/                   # Panel protegido tras iniciar sesión
    │       ├── cuotas/              # Vista de residente: sus cuotas y pagos
    │       ├── administracion/      # Vista de administrador: unidades y cuotas
    │       └── comunicados/         # Avisos: lectura para todos, CRUD para admin
    ├── context/ContextoAutenticacion.tsx
    └── lib/api.ts                   # Cliente HTTP hacia el backend
```

## Cómo correr el backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # Completa URL_BASE_DATOS y CLAVE_SECRETA_JWT
uvicorn app.main:aplicacion --reload
```

La API queda disponible en `http://localhost:8000` y la documentación
interactiva en `http://localhost:8000/docs`.

### Base de datos (Supabase)

1. Crea un proyecto en [Supabase](https://supabase.com).
2. Copia la cadena de conexión (Settings → Database) a `URL_BASE_DATOS` en `.env`.
3. Opcional: ejecuta `backend/supabase/esquema.sql` en el SQL Editor de Supabase,
   o deja que la app cree las tablas automáticamente al iniciar (`create_all`).

## Cómo correr el frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # Ajusta NEXT_PUBLIC_URL_API si es necesario
npm run dev
```

La aplicación queda disponible en `http://localhost:3000`.

## Módulo de cuotas y pagos

- Una **unidad** puede tener cero o un residente asignado (`GET/PATCH /api/unidades`).
- El **administrador** crea cuotas para una unidad (`POST /api/cuotas`) indicando
  concepto, monto y fecha de vencimiento.
- El **residente** solo puede ver y pagar las cuotas de su propia unidad; el
  administrador puede ver y pagar las de cualquier unidad. Esta verificación
  ocurre en `verificar_pertenencia_unidad` (backend), no solo en el frontend.
- Los pagos (`POST /api/cuotas/{id}/pagos`) admiten abonos parciales. El backend
  valida que el monto no exceda el saldo pendiente y recalcula el estado de la
  cuota (`pendiente` → `parcial` → `pagada`) en cada abono.

## Reglas de seguridad aplicadas

- Contraseñas nunca se almacenan en texto plano (hash con **bcrypt**).
- Sesión basada en **JWT** con expiración configurable.
- Validación de fortaleza de contraseña (mínimo 8 caracteres, letras y números)
  y de formato de correo, en el esquema de entrada (Pydantic).
- Endpoints protegidos mediante dependencias de FastAPI
  (`obtener_usuario_actual`, `requerir_rol`) para exigir autenticación y rol.
- CORS restringido a los orígenes configurados explícitamente.

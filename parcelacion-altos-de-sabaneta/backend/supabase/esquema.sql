-- Esquema inicial de base de datos: Parcelación Altos de Sabaneta
-- Pensado para ejecutarse en el SQL Editor de Supabase (Postgres).
-- El backend puede crear estas tablas automáticamente vía SQLAlchemy,
-- pero este script sirve como referencia versionada del modelo de datos.

create extension if not exists "pgcrypto";

-- Tipo de rol de usuario dentro de la parcelación
do $$
begin
    if not exists (select 1 from pg_type where typname = 'rol_usuario') then
        create type rol_usuario as enum ('administrador', 'residente');
    end if;
end
$$;

-- Usuarios con acceso al sistema (administradores y residentes)
create table if not exists usuarios (
    id serial primary key,
    nombre_completo varchar(150) not null,
    correo_electronico varchar(150) not null unique,
    contrasena_hash varchar(255) not null,
    rol rol_usuario not null default 'residente',
    esta_activo boolean not null default true,
    creado_en timestamptz not null default now()
);

create index if not exists idx_usuarios_correo on usuarios (correo_electronico);

-- Unidades habitacionales (casas/lotes) de la parcelación
create table if not exists unidades (
    id serial primary key,
    codigo varchar(50) not null unique,
    residente_id integer references usuarios (id) on delete set null,
    creado_en timestamptz not null default now()
);

-- Estado de una cuota según lo pagado hasta el momento
do $$
begin
    if not exists (select 1 from pg_type where typname = 'estado_cuota') then
        create type estado_cuota as enum ('pendiente', 'parcial', 'pagada');
    end if;
end
$$;

-- Cuotas de mantenimiento (u otro concepto) generadas para una unidad
create table if not exists cuotas (
    id serial primary key,
    unidad_id integer not null references unidades (id) on delete cascade,
    concepto varchar(150) not null,
    monto numeric(12, 2) not null check (monto > 0),
    fecha_vencimiento date not null,
    estado estado_cuota not null default 'pendiente',
    creado_en timestamptz not null default now()
);

create index if not exists idx_cuotas_unidad on cuotas (unidad_id);

-- Abonos (totales o parciales) registrados contra una cuota
create table if not exists pagos (
    id serial primary key,
    cuota_id integer not null references cuotas (id) on delete cascade,
    monto_pagado numeric(12, 2) not null check (monto_pagado > 0),
    metodo_pago varchar(50) not null,
    registrado_por_id integer not null references usuarios (id),
    creado_en timestamptz not null default now()
);

create index if not exists idx_pagos_cuota on pagos (cuota_id);

-- Tablas futuras (fuera del alcance de este módulo, se dejan como referencia
-- para los siguientes módulos: comunicados, reservas de zonas comunes, etc.).
--
-- create table comunicados (...);
-- create table reservas (...);

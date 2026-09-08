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

-- Tablas futuras (fuera del alcance de este módulo, se dejan como referencia
-- para los siguientes módulos: gestión de unidades y cuotas de mantenimiento).
--
-- create table condominios (...);
-- create table unidades (...);
-- create table cuotas (...);

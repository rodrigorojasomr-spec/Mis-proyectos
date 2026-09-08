/** Cliente HTTP simple para hablar con el backend de FastAPI. */

const URL_BASE_API = process.env.NEXT_PUBLIC_URL_API ?? "http://localhost:8000";

export type RolUsuario = "administrador" | "residente";

export interface Usuario {
  id: number;
  nombre_completo: string;
  correo_electronico: string;
  rol: RolUsuario;
  esta_activo: boolean;
}

export interface TokenAcceso {
  token_acceso: string;
  tipo_token: string;
  usuario: Usuario;
}

export class ErrorApi extends Error {
  constructor(public codigoEstado: number, mensaje: string) {
    super(mensaje);
  }
}

/** Envuelve fetch para lanzar un error legible cuando la API responde con un fallo. */
async function solicitar<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const respuesta = await fetch(`${URL_BASE_API}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      ...opciones.headers,
    },
  });

  if (!respuesta.ok) {
    const cuerpoError = await respuesta.json().catch(() => null);
    const mensaje = cuerpoError?.detail ?? "Ocurrió un error al comunicarse con el servidor";
    throw new ErrorApi(respuesta.status, mensaje);
  }

  return respuesta.json() as Promise<T>;
}

export function registrarUsuario(datos: {
  nombre_completo: string;
  correo_electronico: string;
  contrasena: string;
  rol: RolUsuario;
}): Promise<Usuario> {
  return solicitar<Usuario>("/api/autenticacion/registro", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export function iniciarSesion(datos: {
  correo_electronico: string;
  contrasena: string;
}): Promise<TokenAcceso> {
  return solicitar<TokenAcceso>("/api/autenticacion/login", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export function obtenerPerfil(token: string): Promise<Usuario> {
  return solicitar<Usuario>("/api/autenticacion/perfil", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function listarResidentes(token: string): Promise<Usuario[]> {
  return solicitar<Usuario[]>("/api/autenticacion/residentes", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export interface Unidad {
  id: number;
  codigo: string;
  residente_id: number | null;
}

export function crearUnidad(
  token: string,
  datos: { codigo: string; residente_id: number | null }
): Promise<Unidad> {
  return solicitar<Unidad>("/api/unidades", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(datos),
  });
}

export function listarUnidades(token: string): Promise<Unidad[]> {
  return solicitar<Unidad[]>("/api/unidades", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function obtenerMiUnidad(token: string): Promise<Unidad | null> {
  return solicitar<Unidad | null>("/api/unidades/mia", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export type EstadoCuota = "pendiente" | "parcial" | "pagada";

export interface Pago {
  id: number;
  cuota_id: number;
  monto_pagado: string;
  metodo_pago: string;
  registrado_por_id: number;
  creado_en: string;
}

export interface Cuota {
  id: number;
  unidad_id: number;
  concepto: string;
  monto: string;
  fecha_vencimiento: string;
  estado: EstadoCuota;
  saldo_pendiente: string;
  pagos: Pago[];
}

export function crearCuota(
  token: string,
  datos: { unidad_id: number; concepto: string; monto: number; fecha_vencimiento: string }
): Promise<Cuota> {
  return solicitar<Cuota>("/api/cuotas", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(datos),
  });
}

export function listarCuotasPorUnidad(token: string, unidadId: number): Promise<Cuota[]> {
  return solicitar<Cuota[]>(`/api/cuotas/unidad/${unidadId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function registrarPago(
  token: string,
  cuotaId: number,
  datos: { monto_pagado: number; metodo_pago: string }
): Promise<Pago> {
  return solicitar<Pago>(`/api/cuotas/${cuotaId}/pagos`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(datos),
  });
}

export interface Comunicado {
  id: number;
  titulo: string;
  contenido: string;
  destacado: boolean;
  autor_id: number;
  creado_en: string;
  actualizado_en: string;
}

export function listarComunicados(token: string): Promise<Comunicado[]> {
  return solicitar<Comunicado[]>("/api/comunicados", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function crearComunicado(
  token: string,
  datos: { titulo: string; contenido: string; destacado: boolean }
): Promise<Comunicado> {
  return solicitar<Comunicado>("/api/comunicados", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(datos),
  });
}

export function actualizarComunicado(
  token: string,
  comunicadoId: number,
  datos: Partial<{ titulo: string; contenido: string; destacado: boolean }>
): Promise<Comunicado> {
  return solicitar<Comunicado>(`/api/comunicados/${comunicadoId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(datos),
  });
}

/** Elimina un comunicado. No usa solicitar() porque la respuesta 204 no trae cuerpo JSON. */
export async function eliminarComunicado(token: string, comunicadoId: number): Promise<void> {
  const respuesta = await fetch(`${URL_BASE_API}/api/comunicados/${comunicadoId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!respuesta.ok) {
    const cuerpoError = await respuesta.json().catch(() => null);
    throw new ErrorApi(
      respuesta.status,
      cuerpoError?.detail ?? "No se pudo eliminar el comunicado"
    );
  }
}

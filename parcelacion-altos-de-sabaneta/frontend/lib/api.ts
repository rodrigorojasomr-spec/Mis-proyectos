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

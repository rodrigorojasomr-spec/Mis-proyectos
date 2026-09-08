"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { obtenerPerfil, type Usuario } from "@/lib/api";

const CLAVE_TOKEN_ALMACENAMIENTO = "pasab_token_acceso";

interface ValorContextoAutenticacion {
  usuario: Usuario | null;
  token: string | null;
  cargando: boolean;
  iniciarSesionLocal: (token: string, usuario: Usuario) => void;
  cerrarSesion: () => void;
}

const ContextoAutenticacion = createContext<ValorContextoAutenticacion | undefined>(undefined);

/** Provee el estado de sesión (usuario y token) a toda la aplicación. */
export function ProveedorAutenticacion({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const tokenGuardado = window.localStorage.getItem(CLAVE_TOKEN_ALMACENAMIENTO);
    if (!tokenGuardado) {
      setCargando(false);
      return;
    }

    obtenerPerfil(tokenGuardado)
      .then((perfil) => {
        setToken(tokenGuardado);
        setUsuario(perfil);
      })
      .catch(() => {
        window.localStorage.removeItem(CLAVE_TOKEN_ALMACENAMIENTO);
      })
      .finally(() => setCargando(false));
  }, []);

  function iniciarSesionLocal(nuevoToken: string, nuevoUsuario: Usuario) {
    window.localStorage.setItem(CLAVE_TOKEN_ALMACENAMIENTO, nuevoToken);
    setToken(nuevoToken);
    setUsuario(nuevoUsuario);
  }

  function cerrarSesion() {
    window.localStorage.removeItem(CLAVE_TOKEN_ALMACENAMIENTO);
    setToken(null);
    setUsuario(null);
  }

  return (
    <ContextoAutenticacion.Provider value={{ usuario, token, cargando, iniciarSesionLocal, cerrarSesion }}>
      {children}
    </ContextoAutenticacion.Provider>
  );
}

export function useAutenticacion(): ValorContextoAutenticacion {
  const contexto = useContext(ContextoAutenticacion);
  if (!contexto) {
    throw new Error("useAutenticacion debe usarse dentro de ProveedorAutenticacion");
  }
  return contexto;
}

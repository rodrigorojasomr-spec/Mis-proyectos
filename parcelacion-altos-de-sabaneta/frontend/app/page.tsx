"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAutenticacion } from "@/context/ContextoAutenticacion";

/** Página raíz: redirige según si hay sesión activa o no. */
export default function PaginaInicio() {
  const { usuario, cargando } = useAutenticacion();
  const router = useRouter();

  useEffect(() => {
    if (cargando) return;
    router.replace(usuario ? "/panel" : "/iniciar-sesion");
  }, [cargando, usuario, router]);

  return null;
}

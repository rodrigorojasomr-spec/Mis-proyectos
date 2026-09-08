"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAutenticacion } from "@/context/ContextoAutenticacion";

export default function PaginaPanel() {
  const router = useRouter();
  const { usuario, cargando, cerrarSesion } = useAutenticacion();

  useEffect(() => {
    if (!cargando && !usuario) {
      router.replace("/iniciar-sesion");
    }
  }, [cargando, usuario, router]);

  if (cargando || !usuario) {
    return null;
  }

  function manejarCierreSesion() {
    cerrarSesion();
    router.push("/iniciar-sesion");
  }

  return (
    <div>
      <header className="panel-cabecera">
        <div>
          <strong>Parcelación Altos de Sabaneta</strong>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span>{usuario.nombre_completo}</span>
          <span className="insignia-rol">{usuario.rol}</span>
          <button className="boton-primario" style={{ width: "auto" }} onClick={manejarCierreSesion}>
            Cerrar sesión
          </button>
        </div>
      </header>

      <main className="panel-contenido">
        <h2>Bienvenido/a, {usuario.nombre_completo}</h2>
        <p>
          Este es el panel inicial de la parcelación. Próximamente aquí verás la gestión de
          unidades, residentes y cuotas de mantenimiento.
        </p>
      </main>
    </div>
  );
}

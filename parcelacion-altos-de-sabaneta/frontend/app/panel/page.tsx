"use client";

import { useEffect } from "react";
import Link from "next/link";
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

        <div className="seccion">
          <h2>Cuotas y pagos</h2>
          <p>Consulta el estado de las cuotas de mantenimiento y registra tus pagos.</p>
          <Link href="/panel/cuotas" className="enlace-navegacion">
            Ir a mis cuotas →
          </Link>
        </div>

        {usuario.rol === "administrador" && (
          <div className="seccion">
            <h2>Administración</h2>
            <p>Crea unidades, asigna residentes y genera cuotas de mantenimiento.</p>
            <Link href="/panel/administracion" className="enlace-navegacion">
              Ir a administración →
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}

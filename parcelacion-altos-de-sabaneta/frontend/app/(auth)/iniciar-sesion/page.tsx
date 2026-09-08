"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { iniciarSesion, ErrorApi } from "@/lib/api";
import { useAutenticacion } from "@/context/ContextoAutenticacion";

export default function PaginaIniciarSesion() {
  const router = useRouter();
  const { iniciarSesionLocal } = useAutenticacion();

  const [correoElectronico, setCorreoElectronico] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [mensajeError, setMensajeError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function manejarEnvio(evento: FormEvent) {
    evento.preventDefault();
    setMensajeError(null);
    setEnviando(true);

    try {
      const resultado = await iniciarSesion({ correo_electronico: correoElectronico, contrasena });
      iniciarSesionLocal(resultado.token_acceso, resultado.usuario);
      router.push("/panel");
    } catch (error) {
      setMensajeError(error instanceof ErrorApi ? error.message : "No se pudo iniciar sesión");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="contenedor-centrado">
      <div className="tarjeta">
        <h1>Parcelación Altos de Sabaneta</h1>
        <p className="subtitulo">Ingresa con tu correo y contraseña</p>

        {mensajeError && <div className="mensaje-error">{mensajeError}</div>}

        <form onSubmit={manejarEnvio}>
          <div className="campo-formulario">
            <label htmlFor="correo_electronico">Correo electrónico</label>
            <input
              id="correo_electronico"
              type="email"
              required
              value={correoElectronico}
              onChange={(evento) => setCorreoElectronico(evento.target.value)}
              autoComplete="email"
            />
          </div>

          <div className="campo-formulario">
            <label htmlFor="contrasena">Contraseña</label>
            <input
              id="contrasena"
              type="password"
              required
              value={contrasena}
              onChange={(evento) => setContrasena(evento.target.value)}
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="boton-primario" disabled={enviando}>
            {enviando ? "Ingresando..." : "Ingresar"}
          </button>
        </form>

        <Link href="/registro" className="enlace-secundario">
          ¿Aún no tienes cuenta? Regístrate aquí
        </Link>
      </div>
    </div>
  );
}

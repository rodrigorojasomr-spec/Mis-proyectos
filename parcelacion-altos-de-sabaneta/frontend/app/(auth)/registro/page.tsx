"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { registrarUsuario, ErrorApi, type RolUsuario } from "@/lib/api";

export default function PaginaRegistro() {
  const router = useRouter();

  const [nombreCompleto, setNombreCompleto] = useState("");
  const [correoElectronico, setCorreoElectronico] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [rol, setRol] = useState<RolUsuario>("residente");
  const [mensajeError, setMensajeError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function manejarEnvio(evento: FormEvent) {
    evento.preventDefault();
    setMensajeError(null);
    setEnviando(true);

    try {
      await registrarUsuario({
        nombre_completo: nombreCompleto,
        correo_electronico: correoElectronico,
        contrasena,
        rol,
      });
      router.push("/iniciar-sesion");
    } catch (error) {
      setMensajeError(error instanceof ErrorApi ? error.message : "No se pudo completar el registro");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="contenedor-centrado">
      <div className="tarjeta">
        <h1>Crear cuenta</h1>
        <p className="subtitulo">Regístrate como residente o administrador</p>

        {mensajeError && <div className="mensaje-error">{mensajeError}</div>}

        <form onSubmit={manejarEnvio}>
          <div className="campo-formulario">
            <label htmlFor="nombre_completo">Nombre completo</label>
            <input
              id="nombre_completo"
              type="text"
              required
              minLength={3}
              value={nombreCompleto}
              onChange={(evento) => setNombreCompleto(evento.target.value)}
              autoComplete="name"
            />
          </div>

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
              minLength={8}
              value={contrasena}
              onChange={(evento) => setContrasena(evento.target.value)}
              autoComplete="new-password"
            />
          </div>

          <div className="campo-formulario">
            <label htmlFor="rol">Tipo de usuario</label>
            <select id="rol" value={rol} onChange={(evento) => setRol(evento.target.value as RolUsuario)}>
              <option value="residente">Residente</option>
              <option value="administrador">Administrador</option>
            </select>
          </div>

          <button type="submit" className="boton-primario" disabled={enviando}>
            {enviando ? "Creando cuenta..." : "Crear cuenta"}
          </button>
        </form>

        <Link href="/iniciar-sesion" className="enlace-secundario">
          ¿Ya tienes cuenta? Inicia sesión
        </Link>
      </div>
    </div>
  );
}

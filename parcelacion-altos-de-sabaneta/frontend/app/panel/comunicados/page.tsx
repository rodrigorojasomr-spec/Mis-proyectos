"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAutenticacion } from "@/context/ContextoAutenticacion";
import {
  ErrorApi,
  actualizarComunicado,
  crearComunicado,
  eliminarComunicado,
  listarComunicados,
  type Comunicado,
} from "@/lib/api";

function formatearFecha(fechaIso: string): string {
  return new Date(fechaIso).toLocaleString("es-CO", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function PaginaComunicados() {
  const router = useRouter();
  const { usuario, token, cargando } = useAutenticacion();
  const esAdministrador = usuario?.rol === "administrador";

  const [comunicados, setComunicados] = useState<Comunicado[]>([]);
  const [comunicadoEnEdicion, setComunicadoEnEdicion] = useState<Comunicado | null>(null);
  const [titulo, setTitulo] = useState("");
  const [contenido, setContenido] = useState("");
  const [destacado, setDestacado] = useState(false);

  const [mensajeError, setMensajeError] = useState<string | null>(null);
  const [mensajeExito, setMensajeExito] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const cargarComunicados = useCallback(async () => {
    if (!token) return;
    try {
      const lista = await listarComunicados(token);
      setComunicados(lista);
    } catch (error) {
      setMensajeError(
        error instanceof ErrorApi ? error.message : "No se pudieron cargar los comunicados"
      );
    }
  }, [token]);

  useEffect(() => {
    if (!cargando && !usuario) {
      router.replace("/iniciar-sesion");
      return;
    }
    cargarComunicados();
  }, [cargando, usuario, router, cargarComunicados]);

  if (cargando || !usuario) {
    return null;
  }

  function limpiarFormulario() {
    setComunicadoEnEdicion(null);
    setTitulo("");
    setContenido("");
    setDestacado(false);
  }

  function iniciarEdicion(comunicado: Comunicado) {
    setComunicadoEnEdicion(comunicado);
    setTitulo(comunicado.titulo);
    setContenido(comunicado.contenido);
    setDestacado(comunicado.destacado);
    setMensajeError(null);
    setMensajeExito(null);
  }

  async function manejarEnvioFormulario(evento: FormEvent) {
    evento.preventDefault();
    if (!token) return;
    setMensajeError(null);
    setMensajeExito(null);
    setEnviando(true);

    try {
      if (comunicadoEnEdicion) {
        await actualizarComunicado(token, comunicadoEnEdicion.id, { titulo, contenido, destacado });
        setMensajeExito("Comunicado actualizado correctamente");
      } else {
        await crearComunicado(token, { titulo, contenido, destacado });
        setMensajeExito("Comunicado publicado correctamente");
      }
      limpiarFormulario();
      await cargarComunicados();
    } catch (error) {
      setMensajeError(error instanceof ErrorApi ? error.message : "No se pudo guardar el comunicado");
    } finally {
      setEnviando(false);
    }
  }

  async function manejarEliminar(comunicado: Comunicado) {
    if (!token) return;
    if (!window.confirm(`¿Eliminar el comunicado "${comunicado.titulo}"?`)) return;

    setMensajeError(null);
    setMensajeExito(null);

    try {
      await eliminarComunicado(token, comunicado.id);
      setMensajeExito("Comunicado eliminado correctamente");
      await cargarComunicados();
    } catch (error) {
      setMensajeError(error instanceof ErrorApi ? error.message : "No se pudo eliminar el comunicado");
    }
  }

  return (
    <div>
      <header className="panel-cabecera">
        <div>
          <strong>Parcelación Altos de Sabaneta</strong>
        </div>
        <Link href="/panel" className="enlace-navegacion">
          ← Volver al panel
        </Link>
      </header>

      <main className="panel-contenido">
        <h2>Comunicados</h2>

        {mensajeExito && <div className="mensaje-exito">{mensajeExito}</div>}
        {mensajeError && <div className="mensaje-error">{mensajeError}</div>}

        {esAdministrador && (
          <div className="seccion">
            <h2>{comunicadoEnEdicion ? "Editar comunicado" : "Publicar comunicado"}</h2>
            <form onSubmit={manejarEnvioFormulario}>
              <div className="campo-formulario">
                <label htmlFor="titulo_comunicado">Título</label>
                <input
                  id="titulo_comunicado"
                  type="text"
                  required
                  minLength={3}
                  value={titulo}
                  onChange={(evento) => setTitulo(evento.target.value)}
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="contenido_comunicado">Contenido</label>
                <textarea
                  id="contenido_comunicado"
                  required
                  rows={4}
                  value={contenido}
                  onChange={(evento) => setContenido(evento.target.value)}
                  style={{
                    padding: "10px 12px",
                    borderRadius: 8,
                    border: "1px solid var(--color-borde)",
                    fontFamily: "inherit",
                    fontSize: "0.95rem",
                  }}
                />
              </div>

              <div className="campo-formulario" style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
                <input
                  id="destacado_comunicado"
                  type="checkbox"
                  checked={destacado}
                  onChange={(evento) => setDestacado(evento.target.checked)}
                  style={{ width: "auto" }}
                />
                <label htmlFor="destacado_comunicado" style={{ margin: 0 }}>
                  Destacar (aparece primero en la lista)
                </label>
              </div>

              <div style={{ display: "flex", gap: 12 }}>
                <button type="submit" className="boton-primario" style={{ width: "auto" }} disabled={enviando}>
                  {enviando ? "Guardando..." : comunicadoEnEdicion ? "Guardar cambios" : "Publicar"}
                </button>
                {comunicadoEnEdicion && (
                  <button
                    type="button"
                    className="boton-primario"
                    style={{ width: "auto", background: "#8a8f8c" }}
                    onClick={limpiarFormulario}
                  >
                    Cancelar edición
                  </button>
                )}
              </div>
            </form>
          </div>
        )}

        {comunicados.map((comunicado) => (
          <div key={comunicado.id} className="seccion">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <h2 style={{ display: "flex", alignItems: "center", gap: 8 }}>
                {comunicado.titulo}
                {comunicado.destacado && <span className="insignia-rol">Destacado</span>}
              </h2>
              {esAdministrador && (
                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    className="boton-primario"
                    style={{ width: "auto", padding: "6px 14px" }}
                    onClick={() => iniciarEdicion(comunicado)}
                  >
                    Editar
                  </button>
                  <button
                    className="boton-primario"
                    style={{ width: "auto", padding: "6px 14px", background: "var(--color-error)" }}
                    onClick={() => manejarEliminar(comunicado)}
                  >
                    Eliminar
                  </button>
                </div>
              )}
            </div>
            <p style={{ whiteSpace: "pre-wrap" }}>{comunicado.contenido}</p>
            <p style={{ color: "#5b675f", fontSize: "0.8rem", margin: 0 }}>
              Publicado el {formatearFecha(comunicado.creado_en)}
            </p>
          </div>
        ))}

        {comunicados.length === 0 && <p>No hay comunicados publicados todavía.</p>}
      </main>
    </div>
  );
}

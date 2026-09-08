"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAutenticacion } from "@/context/ContextoAutenticacion";
import {
  ErrorApi,
  crearCuota,
  crearUnidad,
  listarCuotasPorUnidad,
  listarResidentes,
  listarUnidades,
  type Cuota,
  type Unidad,
  type Usuario,
} from "@/lib/api";

export default function PaginaAdministracion() {
  const router = useRouter();
  const { usuario, token, cargando } = useAutenticacion();

  const [unidades, setUnidades] = useState<Unidad[]>([]);
  const [residentes, setResidentes] = useState<Usuario[]>([]);
  const [unidadSeleccionadaId, setUnidadSeleccionadaId] = useState<number | null>(null);
  const [cuotasDeUnidad, setCuotasDeUnidad] = useState<Cuota[]>([]);

  const [codigoNuevaUnidad, setCodigoNuevaUnidad] = useState("");
  const [residenteNuevaUnidad, setResidenteNuevaUnidad] = useState<string>("");

  const [conceptoCuota, setConceptoCuota] = useState("");
  const [montoCuota, setMontoCuota] = useState("");
  const [vencimientoCuota, setVencimientoCuota] = useState("");

  const [mensajeError, setMensajeError] = useState<string | null>(null);
  const [mensajeExito, setMensajeExito] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const cargarUnidadesYResidentes = useCallback(async () => {
    if (!token) return;
    try {
      const [listaUnidades, listaResidentes] = await Promise.all([
        listarUnidades(token),
        listarResidentes(token),
      ]);
      setUnidades(listaUnidades);
      setResidentes(listaResidentes);
    } catch (error) {
      setMensajeError(error instanceof ErrorApi ? error.message : "No se pudo cargar la información");
    }
  }, [token]);

  useEffect(() => {
    if (!cargando && (!usuario || usuario.rol !== "administrador")) {
      router.replace("/panel");
      return;
    }
    cargarUnidadesYResidentes();
  }, [cargando, usuario, router, cargarUnidadesYResidentes]);

  useEffect(() => {
    if (!token || unidadSeleccionadaId === null) {
      setCuotasDeUnidad([]);
      return;
    }
    listarCuotasPorUnidad(token, unidadSeleccionadaId)
      .then(setCuotasDeUnidad)
      .catch((error) =>
        setMensajeError(error instanceof ErrorApi ? error.message : "No se pudieron cargar las cuotas")
      );
  }, [token, unidadSeleccionadaId]);

  if (cargando || !usuario || usuario.rol !== "administrador") {
    return null;
  }

  async function manejarCrearUnidad(evento: FormEvent) {
    evento.preventDefault();
    if (!token) return;
    setMensajeError(null);
    setMensajeExito(null);
    setEnviando(true);

    try {
      await crearUnidad(token, {
        codigo: codigoNuevaUnidad,
        residente_id: residenteNuevaUnidad ? Number(residenteNuevaUnidad) : null,
      });
      setMensajeExito("Unidad creada correctamente");
      setCodigoNuevaUnidad("");
      setResidenteNuevaUnidad("");
      await cargarUnidadesYResidentes();
    } catch (error) {
      setMensajeError(error instanceof ErrorApi ? error.message : "No se pudo crear la unidad");
    } finally {
      setEnviando(false);
    }
  }

  async function manejarCrearCuota(evento: FormEvent) {
    evento.preventDefault();
    if (!token || unidadSeleccionadaId === null) return;
    setMensajeError(null);
    setMensajeExito(null);
    setEnviando(true);

    try {
      await crearCuota(token, {
        unidad_id: unidadSeleccionadaId,
        concepto: conceptoCuota,
        monto: Number(montoCuota),
        fecha_vencimiento: vencimientoCuota,
      });
      setMensajeExito("Cuota creada correctamente");
      setConceptoCuota("");
      setMontoCuota("");
      setVencimientoCuota("");
      const cuotasActualizadas = await listarCuotasPorUnidad(token, unidadSeleccionadaId);
      setCuotasDeUnidad(cuotasActualizadas);
    } catch (error) {
      setMensajeError(error instanceof ErrorApi ? error.message : "No se pudo crear la cuota");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div>
      <header className="panel-cabecera">
        <div>
          <strong>Parcelación Altos de Sabaneta — Administración</strong>
        </div>
        <Link href="/panel" className="enlace-navegacion">
          ← Volver al panel
        </Link>
      </header>

      <main className="panel-contenido">
        {mensajeExito && <div className="mensaje-exito">{mensajeExito}</div>}
        {mensajeError && <div className="mensaje-error">{mensajeError}</div>}

        <div className="seccion">
          <h2>Crear unidad</h2>
          <form className="formulario-en-linea" onSubmit={manejarCrearUnidad}>
            <div className="campo-formulario">
              <label htmlFor="codigo_unidad">Código de la unidad</label>
              <input
                id="codigo_unidad"
                type="text"
                required
                placeholder="Ej: Casa 15"
                value={codigoNuevaUnidad}
                onChange={(evento) => setCodigoNuevaUnidad(evento.target.value)}
              />
            </div>

            <div className="campo-formulario">
              <label htmlFor="residente_unidad">Residente (opcional)</label>
              <select
                id="residente_unidad"
                value={residenteNuevaUnidad}
                onChange={(evento) => setResidenteNuevaUnidad(evento.target.value)}
              >
                <option value="">Sin asignar</option>
                {residentes.map((residente) => (
                  <option key={residente.id} value={residente.id}>
                    {residente.nombre_completo}
                  </option>
                ))}
              </select>
            </div>

            <button type="submit" className="boton-primario" disabled={enviando}>
              Crear unidad
            </button>
          </form>
        </div>

        <div className="seccion">
          <h2>Unidades</h2>
          <table className="tabla">
            <thead>
              <tr>
                <th>Código</th>
                <th>Residente</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {unidades.map((unidad) => {
                const residente = residentes.find((r) => r.id === unidad.residente_id);
                return (
                  <tr key={unidad.id}>
                    <td>{unidad.codigo}</td>
                    <td>{residente ? residente.nombre_completo : "Sin asignar"}</td>
                    <td>
                      <button
                        className="boton-primario"
                        style={{ width: "auto", padding: "6px 14px" }}
                        onClick={() => setUnidadSeleccionadaId(unidad.id)}
                      >
                        Ver cuotas
                      </button>
                    </td>
                  </tr>
                );
              })}
              {unidades.length === 0 && (
                <tr>
                  <td colSpan={3}>Aún no hay unidades registradas.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {unidadSeleccionadaId !== null && (
          <div className="seccion">
            <h2>
              Cuotas de{" "}
              {unidades.find((unidad) => unidad.id === unidadSeleccionadaId)?.codigo ?? "la unidad"}
            </h2>

            <form className="formulario-en-linea" onSubmit={manejarCrearCuota}>
              <div className="campo-formulario">
                <label htmlFor="concepto_cuota">Concepto</label>
                <input
                  id="concepto_cuota"
                  type="text"
                  required
                  placeholder="Ej: Cuota mantenimiento septiembre"
                  value={conceptoCuota}
                  onChange={(evento) => setConceptoCuota(evento.target.value)}
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="monto_cuota">Monto</label>
                <input
                  id="monto_cuota"
                  type="number"
                  min="0.01"
                  step="0.01"
                  required
                  value={montoCuota}
                  onChange={(evento) => setMontoCuota(evento.target.value)}
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="vencimiento_cuota">Fecha de vencimiento</label>
                <input
                  id="vencimiento_cuota"
                  type="date"
                  required
                  value={vencimientoCuota}
                  onChange={(evento) => setVencimientoCuota(evento.target.value)}
                />
              </div>

              <button type="submit" className="boton-primario" disabled={enviando}>
                Crear cuota
              </button>
            </form>

            <table className="tabla" style={{ marginTop: 20 }}>
              <thead>
                <tr>
                  <th>Concepto</th>
                  <th>Monto</th>
                  <th>Vence</th>
                  <th>Recargo por mora</th>
                  <th>Saldo pendiente</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {cuotasDeUnidad.map((cuota) => (
                  <tr key={cuota.id}>
                    <td>{cuota.concepto}</td>
                    <td>${cuota.monto}</td>
                    <td>{cuota.fecha_vencimiento}</td>
                    <td>
                      {Number(cuota.recargo_por_mora) > 0
                        ? `$${cuota.recargo_por_mora} (${cuota.dias_mora} d)`
                        : "—"}
                    </td>
                    <td>${cuota.saldo_pendiente}</td>
                    <td>
                      <span className={`insignia-estado ${cuota.estado}`}>{cuota.estado}</span>
                    </td>
                  </tr>
                ))}
                {cuotasDeUnidad.length === 0 && (
                  <tr>
                    <td colSpan={6}>Esta unidad no tiene cuotas registradas.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

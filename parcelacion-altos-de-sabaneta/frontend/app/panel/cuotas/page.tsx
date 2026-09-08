"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAutenticacion } from "@/context/ContextoAutenticacion";
import {
  ErrorApi,
  obtenerMiUnidad,
  listarCuotasPorUnidad,
  registrarPago,
  type Cuota,
  type Unidad,
} from "@/lib/api";

const METODOS_PAGO = ["efectivo", "transferencia", "tarjeta", "consignacion"];

export default function PaginaMisCuotas() {
  const router = useRouter();
  const { usuario, token, cargando } = useAutenticacion();

  const [unidad, setUnidad] = useState<Unidad | null | undefined>(undefined);
  const [cuotas, setCuotas] = useState<Cuota[]>([]);
  const [cuotaSeleccionada, setCuotaSeleccionada] = useState<Cuota | null>(null);
  const [montoPago, setMontoPago] = useState("");
  const [metodoPago, setMetodoPago] = useState(METODOS_PAGO[0]);
  const [mensajeError, setMensajeError] = useState<string | null>(null);
  const [mensajeExito, setMensajeExito] = useState<string | null>(null);
  const [enviandoPago, setEnviandoPago] = useState(false);

  const cargarDatos = useCallback(async () => {
    if (!token) return;
    try {
      const miUnidad = await obtenerMiUnidad(token);
      setUnidad(miUnidad);
      if (miUnidad) {
        const misCuotas = await listarCuotasPorUnidad(token, miUnidad.id);
        setCuotas(misCuotas);
      }
    } catch (error) {
      setMensajeError(error instanceof ErrorApi ? error.message : "No se pudieron cargar las cuotas");
    }
  }, [token]);

  useEffect(() => {
    if (!cargando && !usuario) {
      router.replace("/iniciar-sesion");
      return;
    }
    cargarDatos();
  }, [cargando, usuario, router, cargarDatos]);

  if (cargando || !usuario) {
    return null;
  }

  function abrirFormularioPago(cuota: Cuota) {
    setCuotaSeleccionada(cuota);
    setMontoPago(cuota.saldo_pendiente);
    setMensajeError(null);
    setMensajeExito(null);
  }

  async function manejarEnvioPago(evento: FormEvent) {
    evento.preventDefault();
    if (!token || !cuotaSeleccionada) return;

    setMensajeError(null);
    setMensajeExito(null);
    setEnviandoPago(true);

    try {
      await registrarPago(token, cuotaSeleccionada.id, {
        monto_pagado: Number(montoPago),
        metodo_pago: metodoPago,
      });
      setMensajeExito("Pago registrado correctamente");
      setCuotaSeleccionada(null);
      await cargarDatos();
    } catch (error) {
      setMensajeError(error instanceof ErrorApi ? error.message : "No se pudo registrar el pago");
    } finally {
      setEnviandoPago(false);
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
        <h2>Mis cuotas de mantenimiento</h2>

        {unidad === undefined && <p>Cargando...</p>}

        {unidad === null && (
          <div className="mensaje-error">
            Aún no tienes una unidad asignada. Contacta al administrador de la parcelación.
          </div>
        )}

        {unidad && (
          <>
            <p>
              Unidad: <strong>{unidad.codigo}</strong>
            </p>

            {mensajeExito && <div className="mensaje-exito">{mensajeExito}</div>}
            {mensajeError && !cuotaSeleccionada && <div className="mensaje-error">{mensajeError}</div>}

            <div className="seccion">
              <table className="tabla">
                <thead>
                  <tr>
                    <th>Concepto</th>
                    <th>Monto</th>
                    <th>Vence</th>
                    <th>Saldo pendiente</th>
                    <th>Estado</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {cuotas.map((cuota) => (
                    <tr key={cuota.id}>
                      <td>{cuota.concepto}</td>
                      <td>${cuota.monto}</td>
                      <td>{cuota.fecha_vencimiento}</td>
                      <td>${cuota.saldo_pendiente}</td>
                      <td>
                        <span className={`insignia-estado ${cuota.estado}`}>{cuota.estado}</span>
                      </td>
                      <td>
                        {cuota.estado !== "pagada" && (
                          <button
                            className="boton-primario"
                            style={{ width: "auto", padding: "6px 14px" }}
                            onClick={() => abrirFormularioPago(cuota)}
                          >
                            Pagar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {cuotas.length === 0 && (
                    <tr>
                      <td colSpan={6}>No tienes cuotas registradas todavía.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {cuotaSeleccionada && (
              <div className="seccion">
                <h2>Registrar pago — {cuotaSeleccionada.concepto}</h2>
                {mensajeError && <div className="mensaje-error">{mensajeError}</div>}

                <form className="formulario-en-linea" onSubmit={manejarEnvioPago}>
                  <div className="campo-formulario">
                    <label htmlFor="monto_pago">Monto a pagar</label>
                    <input
                      id="monto_pago"
                      type="number"
                      min="0.01"
                      step="0.01"
                      max={cuotaSeleccionada.saldo_pendiente}
                      required
                      value={montoPago}
                      onChange={(evento) => setMontoPago(evento.target.value)}
                    />
                  </div>

                  <div className="campo-formulario">
                    <label htmlFor="metodo_pago">Método de pago</label>
                    <select
                      id="metodo_pago"
                      value={metodoPago}
                      onChange={(evento) => setMetodoPago(evento.target.value)}
                    >
                      {METODOS_PAGO.map((metodo) => (
                        <option key={metodo} value={metodo}>
                          {metodo}
                        </option>
                      ))}
                    </select>
                  </div>

                  <button type="submit" className="boton-primario" disabled={enviandoPago}>
                    {enviandoPago ? "Registrando..." : "Confirmar pago"}
                  </button>
                  <button
                    type="button"
                    className="boton-primario"
                    style={{ background: "#8a8f8c" }}
                    onClick={() => setCuotaSeleccionada(null)}
                  >
                    Cancelar
                  </button>
                </form>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

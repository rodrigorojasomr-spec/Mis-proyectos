"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAutenticacion } from "@/context/ContextoAutenticacion";
import {
  ErrorApi,
  formatearMoneda,
  obtenerCarteraPorUnidad,
  obtenerCuotasVencidas,
  obtenerResumenReporte,
  type CarteraUnidad,
  type CuotaVencida,
  type ResumenReporte,
} from "@/lib/api";

export default function PaginaReportes() {
  const router = useRouter();
  const { usuario, token, cargando } = useAutenticacion();

  const [resumen, setResumen] = useState<ResumenReporte | null>(null);
  const [cartera, setCartera] = useState<CarteraUnidad[]>([]);
  const [vencidas, setVencidas] = useState<CuotaVencida[]>([]);
  const [mensajeError, setMensajeError] = useState<string | null>(null);

  const cargarReportes = useCallback(async () => {
    if (!token) return;
    try {
      const [datosResumen, datosCartera, datosVencidas] = await Promise.all([
        obtenerResumenReporte(token),
        obtenerCarteraPorUnidad(token),
        obtenerCuotasVencidas(token),
      ]);
      setResumen(datosResumen);
      setCartera(datosCartera);
      setVencidas(datosVencidas);
    } catch (error) {
      setMensajeError(
        error instanceof ErrorApi ? error.message : "No se pudieron cargar los reportes"
      );
    }
  }, [token]);

  useEffect(() => {
    if (!cargando && (!usuario || usuario.rol !== "administrador")) {
      router.replace("/panel");
      return;
    }
    cargarReportes();
  }, [cargando, usuario, router, cargarReportes]);

  if (cargando || !usuario || usuario.rol !== "administrador") {
    return null;
  }

  return (
    <div>
      <header className="panel-cabecera">
        <div>
          <strong>Parcelación Altos de Sabaneta — Reportes</strong>
        </div>
        <Link href="/panel" className="enlace-navegacion">
          ← Volver al panel
        </Link>
      </header>

      <main className="panel-contenido">
        {mensajeError && <div className="mensaje-error">{mensajeError}</div>}

        {resumen && (
          <div className="fila-kpi">
            <div className="tarjeta-kpi">
              <p className="etiqueta-kpi">Monto facturado</p>
              <p className="valor-kpi">{formatearMoneda(resumen.monto_total_facturado)}</p>
            </div>
            <div className="tarjeta-kpi">
              <p className="etiqueta-kpi">Monto recaudado</p>
              <p className="valor-kpi">{formatearMoneda(resumen.monto_total_recaudado)}</p>
            </div>
            <div className={`tarjeta-kpi ${Number(resumen.monto_total_pendiente) > 0 ? "alerta" : ""}`}>
              <p className="etiqueta-kpi">Saldo pendiente</p>
              <p className="valor-kpi">{formatearMoneda(resumen.monto_total_pendiente)}</p>
            </div>
            <div className={`tarjeta-kpi ${resumen.cuotas_vencidas > 0 ? "alerta" : ""}`}>
              <p className="etiqueta-kpi">Cuotas vencidas</p>
              <p className="valor-kpi">{resumen.cuotas_vencidas}</p>
            </div>
          </div>
        )}

        {resumen && (
          <div className="seccion">
            <h2>Cuotas por estado</h2>
            <table className="tabla">
              <thead>
                <tr>
                  <th>Unidades</th>
                  <th>Cuotas emitidas</th>
                  <th>Pendientes</th>
                  <th>Parciales</th>
                  <th>Pagadas</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{resumen.total_unidades}</td>
                  <td>{resumen.total_cuotas_emitidas}</td>
                  <td>
                    <span className="insignia-estado pendiente">{resumen.cuotas_pendientes}</span>
                  </td>
                  <td>
                    <span className="insignia-estado parcial">{resumen.cuotas_parciales}</span>
                  </td>
                  <td>
                    <span className="insignia-estado pagada">{resumen.cuotas_pagadas}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        <div className="seccion">
          <h2>Cartera por unidad</h2>
          <table className="tabla">
            <thead>
              <tr>
                <th>Unidad</th>
                <th>Residente</th>
                <th>Facturado</th>
                <th>Recaudado</th>
                <th>Saldo pendiente</th>
              </tr>
            </thead>
            <tbody>
              {cartera.map((fila) => (
                <tr key={fila.unidad_id}>
                  <td>{fila.codigo_unidad}</td>
                  <td>{fila.residente ?? "Sin asignar"}</td>
                  <td>${fila.monto_facturado}</td>
                  <td>${fila.monto_recaudado}</td>
                  <td>${fila.saldo_pendiente}</td>
                </tr>
              ))}
              {cartera.length === 0 && (
                <tr>
                  <td colSpan={5}>No hay unidades registradas todavía.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="seccion">
          <h2>Cuotas vencidas</h2>
          <table className="tabla">
            <thead>
              <tr>
                <th>Unidad</th>
                <th>Residente</th>
                <th>Concepto</th>
                <th>Venció</th>
                <th>Días vencida</th>
                <th>Saldo pendiente</th>
              </tr>
            </thead>
            <tbody>
              {vencidas.map((fila) => (
                <tr key={fila.cuota_id}>
                  <td>{fila.codigo_unidad}</td>
                  <td>{fila.residente ?? "Sin asignar"}</td>
                  <td>{fila.concepto}</td>
                  <td>{fila.fecha_vencimiento}</td>
                  <td>{fila.dias_vencida}</td>
                  <td>${fila.saldo_pendiente}</td>
                </tr>
              ))}
              {vencidas.length === 0 && (
                <tr>
                  <td colSpan={6}>No hay cuotas vencidas.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}

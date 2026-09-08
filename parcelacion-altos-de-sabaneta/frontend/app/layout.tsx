import type { Metadata } from "next";
import type { ReactNode } from "react";
import { ProveedorAutenticacion } from "@/context/ContextoAutenticacion";
import "./globals.css";

export const metadata: Metadata = {
  title: "Parcelación Altos de Sabaneta",
  description: "Sistema de administración de la Parcelación Altos de Sabaneta",
};

export default function LayoutRaiz({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body>
        <ProveedorAutenticacion>{children}</ProveedorAutenticacion>
      </body>
    </html>
  );
}

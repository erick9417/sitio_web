import "./globals.css";
import Image from "next/image";
import Link from "next/link";

export const metadata = {
  title: "Catálogo Ortomédica",
  description: "Consulta de inventario por bodega con imágenes por SKU",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <header className="bg-white border-b">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
            <Link href="/" className="flex items-center gap-3">
              <Image src="/logo.png" alt="Ortomdica" width={40} height={40} />
              <span className="text-lg font-semibold">Ortomédica</span>
            </Link>
            <span className="ml-auto text-sm">
              <strong className="text-brand-primary">Inventario</strong> • Catálogo con imágenes
            </span>
          </div>
        </header>
        <main className="min-h-[calc(100vh-60px)]">{children}</main>
        <footer className="border-t">
          <div className="max-w-6xl mx-auto px-4 py-6 text-sm text-gray-500">
            © {new Date().getFullYear()} Ortomédica del Ahorro
          </div>
        </footer>
      </body>
    </html>
  );
}

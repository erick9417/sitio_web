# run_scrapers.py
import os
import sys
import asyncio
import argparse
from typing import Callable, Optional

# ---------- util: intentamos importar A y B por nombres posibles ----------
def _import_main(module_names: list[str]) -> Optional[Callable[[bool], "asyncio.Future"]]:
    for name in module_names:
        try:
            mod = __import__(name, fromlist=["main"])
            return getattr(mod, "main")
        except Exception:
            continue
    return None

# Ajusta aquí los nombres de tus archivos si usas otros
MAIN_A = _import_main([
    "scraper_sistema_a_xls",        # alternativo
])
MAIN_B = _import_main([
    "scraper_sistema_b_xls",        # alternativo
])

if MAIN_A is None:
    print("⚠️ No pude importar el main() de Sistema A. Verifica el nombre del archivo.")
if MAIN_B is None:
    print("⚠️ No pude importar el main() de Sistema B. Verifica el nombre del archivo.")

async def run_selected(systems: list[str], debug: bool, stop_on_error: bool):
    results = {}
    if "a" in systems:
        if MAIN_A is None:
            print("❌ Sistema A no disponible (import falló).")
            results["A"] = "not_available"
        else:
            print("\n========== Ejecutando SISTEMA A ==========")
            try:
                await MAIN_A(debug=debug)
                results["A"] = "ok"
            except Exception as e:
                print(f"❌ Error en Sistema A: {e}")
                results["A"] = f"error: {e}"
                if stop_on_error:
                    return results

    if "b" in systems:
        if MAIN_B is None:
            print("❌ Sistema B no disponible (import falló).")
            results["B"] = "not_available"
        else:
            print("\n========== Ejecutando SISTEMA B ==========")
            try:
                await MAIN_B(debug=debug)
                results["B"] = "ok"
            except Exception as e:
                print(f"❌ Error en Sistema B: {e}")
                results["B"] = f"error: {e}"
                if stop_on_error:
                    return results

    return results

def parse_args():
    p = argparse.ArgumentParser(description="Runner único para scrapers de Sistema A y B.")
    p.add_argument("--systems", "-s",
                   default="a,b",
                   help="Qué sistemas correr: 'a', 'b' o 'a,b' (default).")
    p.add_argument("--debug", "-d", action="store_true",
                   help="Mostrar navegador (equivale a PWDEBUG=1).")
    p.add_argument("--stop-on-error", action="store_true",
                   help="Si un sistema falla, detener la ejecución.")
    return p.parse_args()

def main():
    args = parse_args()

    # Permite conjugar con PWDEBUG si lo prefieres
    if args.debug:
        os.environ["PWDEBUG"] = "1"

    systems = [s.strip().lower() for s in args.systems.split(",") if s.strip()]
    # validación básica
    systems = [s for s in systems if s in {"a", "b"}]
    if not systems:
        print("No se seleccionó ningún sistema válido. Usa -s a,b | a | b")
        sys.exit(2)

    results = asyncio.run(run_selected(systems, debug=args.debug, stop_on_error=args.stop_on_error))
    print("\n========== Resumen ==========")
    for k, v in (results or {}).items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()

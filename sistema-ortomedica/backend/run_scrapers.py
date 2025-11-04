# run_scrapers.py
import os
import sys
import asyncio
import argparse
from typing import Callable, Optional

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------- util: intentamos importar A y B por nombres posibles ----------
def _import_main(module_names: list[str]) -> Optional[Callable[[bool], "asyncio.Future"]]:
    for name in module_names:
        try:
            mod = __import__(name, fromlist=["main"])
            main_func = getattr(mod, "main", None)
            if main_func:
                return main_func
        except Exception as e:
            print(f"  Debug: No se pudo importar {name}: {e}")
            continue
    return None

# Ajusta aquí los nombres de tus archivos si usas otros
print("Intentando importar scrapers...")
MAIN_A = _import_main([
    "scrapers.scraper_sistema_a_xls",# si está dentro de backend/scrapers/
    "scraper_sistema_a_xls",        # alternativo (archivo en backend/)
])
MAIN_B = _import_main([
    "scrapers.scraper_sistema_b_xls",# si está dentro de backend/scrapers/
    "scraper_sistema_b_xls",        # alternativo (archivo en backend/)
])

if MAIN_A is None:
    print("⚠️ No pude importar el main() de Sistema A. Verifica el nombre del archivo.")
else:
    print("✅ Sistema A importado correctamente.")
    
if MAIN_B is None:
    print("⚠️ No pude importar el main() de Sistema B. Verifica el nombre del archivo.")
else:
    print("✅ Sistema B importado correctamente.")

# from db_clean import clear_all_inventory  # Evitamos limpiar toda la base en cada corrida (costoso)

async def run_selected(systems: list[str], debug: bool, stop_on_error: bool):
    # Limpiar toda la base antes de cada corrida puede ser costoso y no necesario
    # ya que cada scraper limpia por bodega (clear_store_inventory). Mantén este bloque
    # solo si realmente necesitas un reset completo.
    # print("\n========== Limpiando base de datos ==========")
    # clear_all_inventory()
    # print("✅ Base limpia.")

    results = {}
    tasks = []
    if "a" in systems:
        if MAIN_A is None:
            print("❌ Sistema A no disponible (import falló).")
            results["A"] = "not_available"
        else:
            print("\n⇒ Programando SISTEMA A…")
            tasks.append(MAIN_A(debug=debug))

    if "b" in systems:
        if MAIN_B is None:
            print("❌ Sistema B no disponible (import falló).")
            results["B"] = "not_available"
        else:
            print("\n⇒ Programando SISTEMA B…")
            tasks.append(MAIN_B(debug=debug))

    # Ejecuta en paralelo los sistemas seleccionados
    if tasks:
        print("\n========== Ejecutando scrapers en paralelo ==========")
        try:
            await asyncio.gather(*tasks)
            for s in ("A","B"):
                if s in results and results[s] == "not_available":
                    continue
                results[s] = results.get(s, "ok")
        except Exception as e:
            print(f"❌ Error en ejecución: {e}")
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

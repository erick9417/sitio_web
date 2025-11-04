# scraper_sistema_b_generales.py
import os, re, asyncio, tempfile, contextlib
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from db import ensure_tables, ensure_store
try:
    from core_scraper_xls import process_spreadsheet
except Exception:
    from scrapers.core_scraper_xls import process_spreadsheet

from db import clear_store_inventory  # asegúrate de importarl
# =================== Config ===================
load_dotenv()

SYSTEM_CODE  = "SISTEMA_B"
BASE         = os.getenv("SISTEMA_B_BASE", "https://sistema.grupoargus.co.cr")
LOGIN_URL    = f"{BASE}/Login.aspx"
DEFAULT_URL  = f"{BASE}/Default.aspx"
REPORTES_URL = f"{BASE}/reportesdinamicosGenerales.aspx"  # Reportes Generales

# En B solo hay una bodega (Calderon), no se selecciona manualmente
BODEGAS = {
    "Calderon": 101,   # usa el store_id que quieras para Calderon en B
}

# Encabezados típicos del export de “Generales”
# (si en B el header es "Descripción" en vez de "Decripción", ajusta core_scraper_xls o este mapa)
COLMAP = {
    "system_id":  "Id",
    "sku":        "Código",
    "name":       "decripción",   # ← minúsculas y con el typo del reporte
    "existencia": "Existencia",
    "costo":      "Costo",
    "precio":     "precioventa",  # ← minúsculas
}

# Selectores
USER_SEL     = "#txt_login, #UserName, input[name='usuario']"
PASS_SEL     = "#txt_password, #Password, input[name='password']"
BTN_LOGIN    = "#cmd_ingresar, input[type='submit'][value*='Ingresar'], button:has-text('Ingresar')"

REPORTE_SEL  = "select:has(option:has-text('Reporte de Inventario'))"
BTN_GENERAR  = "input[value='Generar'], button:has-text('Generar')"
EXPORT_BTNS  = (
    "#ContentPlaceHolder1_img_btn_exportar, "
    "input[type='image'][id*='img_btn_exportar'], "
    "button:has-text('Exportar'), input[type='button'][value='Exportar'], "
    "[title='Exportar'], a[title*='Export'], img[src*='export']"
)

# =================== Helpers ===================
async def login(page):
    await page.goto(LOGIN_URL, wait_until="load")
    await page.fill(USER_SEL, os.getenv("SISTEMA_B_USER", ""))
    await page.fill(PASS_SEL, os.getenv("SISTEMA_B_PASS", ""))
    if await page.locator(BTN_LOGIN).count():
        await page.click(BTN_LOGIN)
    else:
        await page.press(PASS_SEL, "Enter")
    try:
        await page.wait_for_url(re.compile(r"/Default\.aspx$"), timeout=15000)
    except:
        await page.goto(DEFAULT_URL, wait_until="load")
    if "Login.aspx" in page.url:
        raise RuntimeError("Login falló en Sistema B (credenciales/captcha).")

async def download_report(page):
    # Ir a Generales
    await page.goto(REPORTES_URL, wait_until="domcontentloaded")
    await page.wait_for_load_state("networkidle")

    # Seleccionar “Reporte de Inventario” si el combo existe (tolerante a postback)
    rep_sel = page.locator(REPORTE_SEL).first
    if await rep_sel.count():
        try:
            await rep_sel.select_option(label="Reporte de Inventario")
        except Exception:
            pass
        # estabiliza tras posible postback
        await page.wait_for_load_state("load")
        await page.wait_for_load_state("networkidle")

    # En B NO seleccionamos bodega (Calderon por defecto)

    # --- Generar: sin usar .count(); reintenta si hay navegación/postback ---
    for _ in range(6):
        try:
            gen = page.locator(BTN_GENERAR).first
            await gen.wait_for(state="visible", timeout=8000)
            try:
                async with page.expect_navigation(wait_until="networkidle", timeout=25000):
                    await gen.click()
            except Exception:
                # si no hubo navegación, igualmente espera estabilidad
                await page.wait_for_load_state("networkidle")
            break
        except Exception:
            # si el DOM se re-creó por postback, reintenta
            await page.wait_for_load_state("load")
            await page.wait_for_timeout(500)
    else:
        raise RuntimeError("No pude hacer clic en 'Generar' en Sistema B.")

    # --- Exportar: mismo enfoque tolerante ---
    export_btn = page.locator(EXPORT_BTNS).first
    await export_btn.wait_for(state="visible", timeout=20000)
    async with page.expect_download(timeout=90000) as dl:
        await export_btn.click()
    download = await dl.value

    suggested = download.suggested_filename or "reporte_b.xls"
    path = await download.path()
    if path:
        with open(path, "rb") as f:
            return f.read(), suggested

    # Fallback: save_as si el driver no expone path()
    tmp = os.path.join(tempfile.gettempdir(), suggested)
    await download.save_as(tmp)
    with open(tmp, "rb") as f:
        data = f.read()
    with contextlib.suppress(Exception):
        os.remove(tmp)
    return data, suggested

# =================== Main ===================
async def main(debug: bool = False):
    # Ensure DB tables exist when running (defer from import time)
    ensure_tables()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not debug, slow_mo=400 if debug else 0)
        ctx = await browser.new_context(
            accept_downloads=True,
            viewport={"width": 1440, "height": 950},
            timezone_id="America/Costa_Rica",
            locale="es-CR",
        )
        page = await ctx.new_page()
        # Agiliza: bloquea recursos no esenciales
        await ctx.route("**/*", lambda route: route.abort() if route.request.resource_type in {"image","font","media","stylesheet"} else route.continue_())
        page.set_default_timeout(20000)

        await login(page)

        # Iteramos igual para mantener compatibilidad con tu patrón
        for bodega_name, store_id in BODEGAS.items():
            ensure_store(store_id, bodega_name)

            # limpiar previamente SOLO esta bodega de este sistema
            clear_store_inventory(SYSTEM_CODE, store_id)

            print(f"\n=== {SYSTEM_CODE} | Bodega: {bodega_name} ===")
            data, fname = await download_report(page)
            total = process_spreadsheet(data, fname, SYSTEM_CODE, store_id, COLMAP)
            print(f"[{SYSTEM_CODE}] {bodega_name} → {total} filas procesadas")

        await ctx.close()
        await browser.close()

if __name__ == "__main__":
    debug = (os.getenv("PWDEBUG") == "1")
    asyncio.run(main(debug=debug))

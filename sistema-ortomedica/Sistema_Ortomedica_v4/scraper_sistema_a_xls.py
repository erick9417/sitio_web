# scraper_sistema_a_generales.py
import os, re, asyncio, tempfile, contextlib, unicodedata
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from db import ensure_tables, ensure_store
from core_scraper_xls import process_spreadsheet

from db import clear_store_inventory
# =================== Configuración ===================
load_dotenv()
ensure_tables()

SYSTEM_CODE  = "SISTEMA_A"
BASE         = os.getenv("SISTEMA_A_BASE", "https://sistema.grupoargus.co.cr")
LOGIN_URL    = f"{BASE}/Login.aspx"
DEFAULT_URL  = f"{BASE}/Default.aspx"
REPORTES_URL = f"{BASE}/reportesdinamicosGenerales.aspx"  # Reportes Generales

# Bodegas que exige el Sistema A (usa tus IDs reales)
BODEGAS = {
    "HOSPITAL DE NIÑOS": 1,
    "BODEGA":            3,
}

# En Reportes Generales el select de bodega tiene estos values (HTML real)
# <select id="MainContent_grid_parametros_ddl_0_0"> <option value="6">HOSPITAL DE NIÑOS</option> <option value="11">BODEGA</option> </select>
VALUES_BY_BODEGA = {
    "HOSPITAL DE NIÑOS": "6",
    "BODEGA":            "11",
}

# Encabezados del export en Generales (nota el typo Decripción)
COLMAP = {
    "system_id":  "Id",
    "sku":        "Código",
    "name":       "Decripción",
    "existencia": "Existencia",
    "costo":      "Costo",
    "precio":     "PrecioVenta",
}

# Selectores
USER_SEL     = "#txt_login"
PASS_SEL     = "#txt_password"
BTN_LOGIN    = "#cmd_ingresar"
REPORTE_SEL  = "select:has(option:has-text('Reporte de Inventario'))"
BTN_GENERAR  = "input[value='Generar'], button:has-text('Generar')"
EXPORT_BTNS  = (
    "#ContentPlaceHolder1_img_btn_exportar, "
    "input[type='image'][id*='img_btn_exportar'], "
    "button:has-text('Exportar'), input[type='button'][value='Exportar'], "
    "[title='Exportar'], a[title*='Export'], img[src*='export']"
)
BODEGA_SELECT_ID = "#MainContent_grid_parametros_ddl_0_0"

# =================== Helpers ===================
def _norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn")
    return " ".join(s.split()).lower()

async def login(page):
    await page.goto(LOGIN_URL, wait_until="load")
    await page.fill(USER_SEL, os.getenv("SISTEMA_A_USER", ""))
    await page.fill(PASS_SEL, os.getenv("SISTEMA_A_PASS", ""))
    if await page.locator(BTN_LOGIN).count():
        await page.click(BTN_LOGIN)
    else:
        await page.press(PASS_SEL, "Enter")
    try:
        await page.wait_for_url(re.compile(r"/Default\.aspx$"), timeout=15000)
    except:
        await page.goto(DEFAULT_URL, wait_until="load")
    if "Login.aspx" in page.url:
        raise RuntimeError("Login falló en Sistema A (credenciales/captcha).")

async def select_bodega_generales(page, bodega_name: str):
    """Selecciona la bodega por VALUE en el select conocido y verifica."""
    sel = page.locator(BODEGA_SELECT_ID).first
    await sel.wait_for(state="visible", timeout=15000)

    value = VALUES_BY_BODEGA.get(bodega_name)
    if not value:
        # fallback: encontrar value por texto de la opción
        el = await sel.element_handle()
        value = await page.evaluate(
            """(s, target)=>{
                const norm=t=>(t||'').normalize('NFD').replace(/\p{Mn}/gu,'').replace(/\s+/g,' ').trim().toLowerCase();
                for(const o of Array.from(s.options||[])){
                    if(norm(o.textContent)===target) return o.value;
                }
                return null;
            }""",
            el, _norm(bodega_name)
        )
        if not value:
            raise RuntimeError(f"No encontré opción para la bodega: {bodega_name}")

    await sel.select_option(value=value)
    with contextlib.suppress(Exception):
        el = await sel.element_handle()
        if el:
            await page.evaluate("(s)=>s.dispatchEvent(new Event('change',{bubbles:true}))", el)
    await page.wait_for_load_state("networkidle")

    # Verificación de que quedó seleccionada
    with contextlib.suppress(Exception):
        el = await sel.element_handle()
        chosen = await page.evaluate("(s)=>s.options[s.selectedIndex].textContent.trim()", el)
        if _norm(chosen) != _norm(bodega_name):
            # último recurso: setear por JS y disparar change
            await page.evaluate("(s,val)=>{s.value=val; s.dispatchEvent(new Event('change',{bubbles:true}));}", el, value)
            await page.wait_for_load_state("networkidle")

async def download_report(page, bodega_name: str):
    await page.goto(REPORTES_URL, wait_until="domcontentloaded")
    await page.wait_for_load_state("networkidle")

    # Seleccionar “Reporte de Inventario” si el combo existe
    rep_sel = page.locator(REPORTE_SEL).first
    if await rep_sel.count():
        with contextlib.suppress(Exception):
            await rep_sel.select_option(label="Reporte de Inventario")
            await page.wait_for_load_state("networkidle")

    # Seleccionar bodega
    await select_bodega_generales(page, bodega_name)

    # Generar (puede navegar o hacer postback)
    gen = page.locator(BTN_GENERAR).first
    if await gen.count():
        try:
            async with page.expect_navigation(wait_until="networkidle", timeout=30000):
                await gen.click()
        except Exception:
            await page.wait_for_load_state("networkidle")

    # Exportar
    export_btn = page.locator(EXPORT_BTNS).first
    await export_btn.wait_for(state="visible", timeout=20000)
    async with page.expect_download(timeout=90000) as dl:
        await export_btn.click()
    download = await dl.value

    suggested = download.suggested_filename or "reporte.xls"
    path = await download.path()
    if path:
        with open(path, "rb") as f:
            return f.read(), suggested

    # Fallback: save_as
    tmp = os.path.join(tempfile.gettempdir(), suggested)
    await download.save_as(tmp)
    with open(tmp, "rb") as f:
        data = f.read()
    with contextlib.suppress(Exception):
        os.remove(tmp)
    return data, suggested

# =================== Main ===================
async def main(debug: bool = False):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not debug, slow_mo=400 if debug else 0)
        ctx = await browser.new_context(
            accept_downloads=True,
            viewport={"width": 1440, "height": 950},
            timezone_id="America/Costa_Rica",
            locale="es-CR",
        )
        page = await ctx.new_page()

        await login(page)

        for bodega_name, store_id in BODEGAS.items():
            ensure_store(store_id, bodega_name)

            # limpiar previamente SOLO esta bodega de este sistema
            clear_store_inventory(SYSTEM_CODE, store_id)

            print(f"\n=== {SYSTEM_CODE} | Bodega: {bodega_name} ===")
            data, fname = await download_report(page, bodega_name)
            total = process_spreadsheet(data, fname, SYSTEM_CODE, store_id, COLMAP)
            print(f"[{SYSTEM_CODE}] {bodega_name} → {total} filas procesadas")

        await ctx.close()
        await browser.close()
if __name__ == "__main__":
    debug = (os.getenv("PWDEBUG") == "1")
    asyncio.run(main(debug=debug))

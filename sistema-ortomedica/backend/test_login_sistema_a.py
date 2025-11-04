"""
Helper to test login for SISTEMA_A from the console.
Saves a screenshot and page HTML to inspect what's happening (captcha, error messages, etc.).
Run with the backend venv active:

python test_login_sistema_a.py         # headless
python test_login_sistema_a.py -d      # visible browser (debug)

Outputs: login_screenshot.png and login_page.html in the backend folder.
"""
import os
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

BASE = os.getenv("SISTEMA_A_BASE", "https://sistema.grupoargus.co.cr")
LOGIN_URL = f"{BASE}/Login.aspx"
DEFAULT_URL = f"{BASE}/Default.aspx"
USER_SEL = "#txt_login"
PASS_SEL = "#txt_password"
BTN_LOGIN = "#cmd_ingresar"

async def run(debug: bool):
    out_dir = Path(__file__).parent
    screenshot = out_dir / "login_screenshot.png"
    html_out = out_dir / "login_page.html"

    user = os.getenv("SISTEMA_A_USER", "")
    pwd = os.getenv("SISTEMA_A_PASS", "")
    if not user or not pwd:
        print("⚠️ No hay credenciales en las variables de entorno SISTEMA_A_USER/SISTEMA_A_PASS")
        return 1

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not debug)
        ctx = await browser.new_context(viewport={"width": 1366, "height": 900})
        page = await ctx.new_page()
        await page.goto(LOGIN_URL, wait_until="load")
        print("Opened", LOGIN_URL)
        # fill and submit
        try:
            await page.fill(USER_SEL, user)
            await page.fill(PASS_SEL, pwd)
            if await page.locator(BTN_LOGIN).count():
                await page.click(BTN_LOGIN)
            else:
                await page.press(PASS_SEL, "Enter")
            # wait a bit
            await page.wait_for_timeout(5000)
        except Exception as e:
            print("⚠️ Error while filling/submitting login:", e)

        # Save screenshot and html for inspection
        try:
            await page.screenshot(path=str(screenshot), full_page=True)
            content = await page.content()
            html_out.write_text(content, encoding="utf-8")
            print(f"Saved screenshot -> {screenshot}")
            print(f"Saved page html -> {html_out}")
            print("Current URL:", page.url)
        except Exception as e:
            print("⚠️ Error saving artifacts:", e)

        await ctx.close()
        await browser.close()
    return 0

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-d', '--debug', action='store_true', help='Show browser window')
    args = p.parse_args()
    code = asyncio.run(run(debug=args.debug))
    raise SystemExit(code)

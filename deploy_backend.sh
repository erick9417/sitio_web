#!/bin/bash
# Script para instalar dependencias del backend

echo "=== Activando entorno virtual ==="
source ~/venvs/ortomedica/bin/activate

echo "=== Actualizando pip ==="
pip install --upgrade pip

echo "=== Instalando dependencias del backend ==="
cd ~/sistema.ortomedicacr.com/sistema-ortomedica/backend/
pip install -r requirements.txt

echo "=== Instalando Playwright Chromium ==="
playwright install chromium

echo "=== Verificando instalación ==="
pip list | grep -E "(fastapi|uvicorn|playwright|mysql)"

echo ""
echo "=== Instalación completada ==="
echo "Siguiente paso: Verificar base de datos y crear tablas"

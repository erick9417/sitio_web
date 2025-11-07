#!/bin/bash

echo "============================================"
echo "AUDITORÍA DEL SERVIDOR - Sistema Ortomedica"
echo "============================================"
echo ""

echo "1. Directorio actual:"
pwd
echo ""

echo "2. Usuario actual:"
whoami
echo ""

echo "3. Sistema operativo:"
cat /etc/os-release | grep -E "PRETTY_NAME|VERSION"
echo ""

echo "4. Contenido del home:"
ls -lah ~/ | head -20
echo ""

echo "5. Contenido de public_html:"
if [ -d ~/public_html ]; then
    ls -lah ~/public_html/
else
    echo "No existe ~/public_html"
fi
echo ""

echo "6. Dominios configurados:"
if [ -d ~/public_html ]; then
    find ~/public_html -maxdepth 2 -type d | head -10
fi
echo ""

echo "7. Procesos Node/Python activos:"
ps aux | grep -E "node|python|uvicorn" | grep -v grep || echo "Ninguno encontrado"
echo ""

echo "8. Versiones instaladas:"
echo -n "Python: " && python3 --version 2>&1 || echo "No instalado"
echo -n "Node: " && node --version 2>&1 || echo "No instalado"
echo -n "npm: " && npm --version 2>&1 || echo "No instalado"
echo -n "git: " && git --version 2>&1 || echo "No instalado"
echo ""

echo "9. PM2 status:"
pm2 list 2>&1 || echo "PM2 no instalado o no corriendo"
echo ""

echo "10. Espacio en disco:"
df -h ~
echo ""

echo "============================================"
echo "FIN DE AUDITORÍA"
echo "============================================"

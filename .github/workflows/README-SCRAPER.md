# Sistema A Scraper - GitHub Actions

Este workflow ejecuta automáticamente el scraper de inventario de Sistema A usando Playwright en GitHub Actions y sube los datos al servidor.

## 📅 Horario de Ejecución

- **Frecuencia**: Cada hora (13 veces al día)
- **Días**: Lunes a Viernes
- **Horario**: 7:00 AM - 7:00 PM (hora Costa Rica)
- **Cron**: `0 13-22 * * 1-5` (UTC)

## 🔐 Secretos Requeridos

Debes configurar estos secretos en GitHub: **Settings → Secrets and variables → Actions → New repository secret**

### 1. `SISTEMA_A_USER`
- **Descripción**: Usuario para login en Sistema A (Grupo Argus)
- **Ejemplo**: `usuario@ortomedica.com`

### 2. `SISTEMA_A_PASS`
- **Descripción**: Contraseña para Sistema A
- **Ejemplo**: `MiContraseñaSegura123`

### 3. `SERVER_HOST`
- **Descripción**: Hostname o IP del servidor donde se subirá la base de datos
- **Ejemplo**: `sistema.ortomedicacr.com` o `IP_DEL_SERVIDOR`

### 4. `SERVER_USER`
- **Descripción**: Usuario SSH del servidor
- **Ejemplo**: `ortome5`

### 5. `SERVER_SSH_KEY`
- **Descripción**: Llave privada SSH para conectarse al servidor (formato completo, incluyendo BEGIN/END)
- **Cómo obtenerla**:
  ```bash
  # En tu máquina local, genera una nueva llave SSH para GitHub Actions:
  ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_actions_key -N ""
  
  # Copia la llave PÚBLICA al servidor:
  ssh-copy-id -i ~/.ssh/github_actions_key.pub ortome5@sistema.ortomedicacr.com
  
  # Copia la llave PRIVADA (todo el contenido del archivo):
  cat ~/.ssh/github_actions_key
  ```
- **Formato**:
  ```
  -----BEGIN OPENSSH PRIVATE KEY-----
  b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
  ... (múltiples líneas) ...
  -----END OPENSSH PRIVATE KEY-----
  ```

### 6. `SERVER_PATH`
- **Descripción**: Ruta absoluta donde se guardará `inventario.db` en el servidor
- **Ejemplo**: `/home/ortome5/sistema.ortomedicacr.com/sistema-ortomedica/backend`

## 🚀 Uso

### Ejecución Manual
1. Ve a **Actions** en GitHub
2. Selecciona **"Sistema A Scraper (Playwright)"**
3. Click en **"Run workflow"** → **"Run workflow"**
4. Espera ~3-5 minutos

### Ejecución Automática
El workflow se ejecuta automáticamente según el horario configurado.

### Ver Resultados
1. **Actions** → Click en la ejecución más reciente
2. Ver logs del job `scrape-and-upload`
3. Descargar artifact `inventario-db-XXX` si necesitas la base de datos local

## 📊 Consumo de Minutos

- **Ejecuciones**: 13/día × 5 días = 65/semana → ~281/mes
- **Tiempo por ejecución**: ~5 minutos
- **Total mensual**: ~1,405 minutos
- **Plan gratuito**: 2,000 minutos/mes
- **Margen**: ~600 minutos disponibles ✅

## 🔧 Troubleshooting

### Error: "Login falló"
- Verifica que `SISTEMA_A_USER` y `SISTEMA_A_PASS` sean correctos
- Sistema A puede tener captcha activado

### Error: "Permission denied (publickey)"
- Verifica que `SERVER_SSH_KEY` contenga la llave privada completa
- Verifica que la llave pública esté en `~/.ssh/authorized_keys` del servidor

### Error: "No such file or directory"
- Verifica que `SERVER_PATH` sea la ruta correcta y exista

### Base de datos no se actualiza
- Verifica que el archivo `inventario.db` tenga permisos de escritura
- Verifica que el usuario SSH tenga permisos en la carpeta

## 📝 Notas

- La base de datos se reemplaza **atómicamente** (primero `.new`, luego `mv`)
- Los artifacts se retienen **1 día** (ajustable en el workflow)
- El scraper limpia inventario previo antes de insertar nuevos datos
- Se bloquean recursos no esenciales (imágenes, fonts) para acelerar scraping

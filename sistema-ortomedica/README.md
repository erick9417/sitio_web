# Sistema Ortomedica - Comparador de Precios

Sistema de comparación de precios e inventario entre diferentes sitios web.

## Estructura del Proyecto

```
sistema-ortomedica/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
└── README.md
```

## Requisitos

- Node.js 18+
- Python 3.8+
- MySQL

## Instalación

1. Instalar dependencias del backend:
```bash
cd backend
pip install -r requirements.txt
```

2. Instalar dependencias del frontend:
```bash
cd frontend
npm install
```

## Desarrollo

Para ejecutar en modo desarrollo:

```bash
npm run dev
```

Esto iniciará:
- Frontend en http://localhost:3000
- Backend en http://localhost:8000

## Variables de Entorno

### Backend (.env)
```
DB_HOST=localhost
DB_USER=root
DB_PASS=your_password
DB_NAME=inventarios
DB_PORT=3306
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
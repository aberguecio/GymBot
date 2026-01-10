# GymBot - Telegram Bot para Tracking de Gimnasio

GymBot es un bot de Telegram completamente dockerizado que te permite llevar un control de tus entrenamientos en el gimnasio. Incluye una API REST construida con FastAPI y un bot interactivo de Telegram.

## Características

- ✅ **Bot de Telegram** con comandos interactivos
- ✅ **API REST** con FastAPI
- ✅ **Base de datos PostgreSQL**
- ✅ **Completamente dockerizado**
- ✅ **Integración con Traefik** para SSL/HTTPS
- ✅ **Migraciones automáticas** con Alembic

## Requisitos

- Docker y Docker Compose
- Un dominio con SSL (para webhook de Telegram)
- Traefik configurado (o cualquier reverse proxy)

## Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd GymBot
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus valores:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8454553246:AAF9H6peceoH6b-qBMH0WAakL7VEsscYKGA
TELEGRAM_WEBHOOK_URL=https://gymbot.berguecio.cl
TELEGRAM_WEBHOOK_PATH=/webhook/telegram

# Database Configuration
POSTGRES_PASSWORD=tu_password_seguro_aqui
DATABASE_URL=postgresql+asyncpg://gymbot:tu_password_seguro_aqui@db:5432/gymbot

# API Security
API_KEY=tu_api_key_secreta_aqui

# Application Settings
DEBUG=false
```

### 3. Verificar red de Traefik

```bash
docker network ls | grep proxy
```

Si no existe, crear la red:

```bash
docker network create proxy
```

### 4. Levantar los contenedores

```bash
docker-compose up -d --build
```

### 5. Verificar logs

```bash
docker-compose logs -f app
```

## Comandos del Bot

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Registro inicial y bienvenida | `/start` |
| `/help` | Muestra ayuda | `/help` |
| `/add <descripción>` | Registra ejercicio de hoy | `/add Bench press 3x10, Cardio 20min` |
| `/stats` | Estadísticas del mes actual | `/stats` |
| `/stats_month <YYYY-MM>` | Estadísticas de un mes específico | `/stats_month 2025-12` |
| `/stats_custom <inicio> <fin>` | Estadísticas de rango custom | `/stats_custom 2026-01-01 2026-01-15` |

## API Endpoints

### 1. Crear Usuario

```bash
POST /api/v1/users
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
    "telegram_id": 123456789,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe"
}
```

### 2. Agregar Ejercicio

```bash
POST /api/v1/exercises
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
    "telegram_id": 123456789,
    "day": "2026-01-10",
    "description": "Bench press 3x10, Squats 4x8"
}
```

### 3. Obtener Conteo de Ejercicios

```bash
# Por mes
GET /api/v1/exercises/count?telegram_id=123456789&month=2026-01
Authorization: Bearer <API_KEY>

# Por rango de fechas
GET /api/v1/exercises/count?telegram_id=123456789&start_date=2026-01-01&end_date=2026-01-31
Authorization: Bearer <API_KEY>

# Todos los usuarios
GET /api/v1/exercises/count?month=2026-01
Authorization: Bearer <API_KEY>
```

## Comandos Docker

```bash
# Levantar contenedores
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Ver status
docker-compose ps

# Ejecutar migraciones manualmente
docker-compose exec app alembic upgrade head

# Detener contenedores
docker-compose down

# Limpiar volúmenes (⚠️ borra datos)
docker-compose down -v

# Rebuild
docker-compose up -d --build
```

## Verificación

### 1. Health Check

```bash
curl https://gymbot.berguecio.cl/health
```

### 2. Verificar Webhook de Telegram

```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

### 3. Documentación de API

Visita: `https://gymbot.berguecio.cl/docs`

## Estructura del Proyecto

```
GymBot/
├── app/
│   ├── api/          # Endpoints de FastAPI
│   ├── bot/          # Handlers del bot de Telegram
│   ├── models/       # Modelos SQLAlchemy
│   ├── schemas/      # Schemas Pydantic
│   ├── services/     # Lógica de negocio
│   ├── config.py     # Configuración
│   ├── database.py   # Setup de base de datos
│   └── main.py       # Aplicación principal
├── alembic/          # Migraciones de base de datos
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Base de Datos

### Backup

```bash
docker-compose exec db pg_dump -U gymbot gymbot > backup.sql
```

### Restaurar

```bash
docker-compose exec -T db psql -U gymbot gymbot < backup.sql
```

### Acceder a PostgreSQL

```bash
docker-compose exec db psql -U gymbot -d gymbot
```

## Troubleshooting

### El webhook no funciona

1. Verificar que el dominio apunta a tu servidor
2. Verificar que Traefik está corriendo
3. Verificar los logs: `docker-compose logs -f app`
4. Verificar webhook info con la API de Telegram

### Error de conexión a la base de datos

1. Verificar que el contenedor de db está corriendo: `docker-compose ps`
2. Verificar variables de entorno en `.env`
3. Ver logs de db: `docker-compose logs -f db`

### Migraciones no se aplican

```bash
# Ejecutar manualmente
docker-compose exec app alembic upgrade head

# Ver estado
docker-compose exec app alembic current
```

## Desarrollo

Para desarrollo local sin webhook:

1. Cambiar a modo polling en `app/main.py` (comentar webhook, usar polling)
2. No necesitas dominio público
3. Usar SQLite: `DATABASE_URL=sqlite+aiosqlite:///./gymbot.db`

## Licencia

MIT

## Soporte

Para reportar bugs o solicitar features, abre un issue en el repositorio.

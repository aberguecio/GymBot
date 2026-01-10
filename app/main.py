from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.api import users, exercises
from app.bot import handlers

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize Telegram bot application
telegram_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown"""
    # Startup
    logger.info("Starting GymBot application...")

    # Register bot command handlers
    telegram_app.add_handler(CommandHandler("start", handlers.start_command))
    telegram_app.add_handler(CommandHandler("help", handlers.help_command))
    telegram_app.add_handler(CommandHandler("add", handlers.add_command))
    telegram_app.add_handler(CommandHandler("stats", handlers.stats_command))
    telegram_app.add_handler(CommandHandler("stats_month", handlers.stats_month_command))
    telegram_app.add_handler(CommandHandler("stats_custom", handlers.stats_custom_command))

    # Register error handler
    telegram_app.add_error_handler(handlers.error_handler)

    # Initialize bot
    await telegram_app.initialize()
    await telegram_app.start()

    # Set webhook
    webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}{settings.TELEGRAM_WEBHOOK_PATH}"
    await telegram_app.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to: {webhook_url}")

    logger.info("GymBot application started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down GymBot application...")
    await telegram_app.stop()
    await telegram_app.shutdown()
    logger.info("GymBot application stopped.")


# Create FastAPI app
app = FastAPI(
    title="GymBot API",
    description="API for GymBot - Telegram bot for tracking gym exercises",
    version="1.0.0",
    lifespan=lifespan
)


# Telegram webhook endpoint
@app.post(settings.TELEGRAM_WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """Handle incoming updates from Telegram"""
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"ok": False, "error": str(e)}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GymBot",
        "version": "1.0.0"
    }


# Include API routers
app.include_router(
    users.router,
    prefix=f"{settings.API_PREFIX}/users",
    tags=["users"]
)

app.include_router(
    exercises.router,
    prefix=f"{settings.API_PREFIX}/exercises",
    tags=["exercises"]
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to GymBot API",
        "docs": "/docs",
        "health": "/health"
    }

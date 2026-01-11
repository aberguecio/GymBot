from telegram import Update
from telegram.ext import ContextTypes
from datetime import date
from dateutil.relativedelta import relativedelta
from app.services import user_service, exercise_service
from app.database import AsyncSessionLocal
from app.bot.utils import parse_date, parse_month, format_exercise_list


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Register user and show welcome message"""
    user = update.effective_user

    async with AsyncSessionLocal() as db:
        # Create or update user
        await user_service.create_or_update_user(
            db=db,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

    await update.message.reply_text(
        "¡Bienvenido a GymBot! 🏋️\n\n"
        "Te ayudaré a llevar el control de tus entrenamientos.\n\n"
        "Tu cuenta ha sido creada exitosamente.\n\n"
        "Comandos disponibles:\n"
        "/add <ejercicio> - Registrar entrenamiento de hoy\n"
        "/stats - Ver estadísticas del mes\n"
        "/stats_month <YYYY-MM> - Ver estadísticas de un mes\n"
        "/stats_custom <inicio> <fin> - Ver estadísticas personalizadas\n"
        "/help - Ver todos los comandos"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "📋 *Comandos de GymBot*\n\n"
        "/start - Iniciar y registrarse\n"
        "/add <ejercicio> - Registrar entrenamiento de hoy\n"
        "   Ejemplo: /add Bench press 3x10, Cardio 20min\n\n"
        "/stats - Ver estadísticas del mes actual\n"
        "/stats_month <YYYY-MM> - Ver estadísticas de un mes específico\n"
        "   Ejemplo: /stats_month 2025-12\n\n"
        "/stats_custom <inicio> <fin> - Ver estadísticas de rango personalizado\n"
        "   Ejemplo: /stats_custom 2026-01-01 2026-01-15\n\n"
        "/help - Mostrar esta ayuda",
        parse_mode="Markdown"
    )


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command - Add exercise for today"""
    if not context.args:
        await update.message.reply_text(
            "❌ Debes proporcionar una descripción del ejercicio.\n\n"
            "Ejemplo: /add Bench press 3x10, Cardio 20min"
        )
        return

    description = " ".join(context.args)
    telegram_id = update.effective_user.id
    today = date.today()

    async with AsyncSessionLocal() as db:
        try:
            # Add exercise
            await exercise_service.add_exercise(
                db=db,
                telegram_id=telegram_id,
                day=today,
                description=description
            )

            # Get count for current month
            month_start = today.replace(day=1)
            counts = await exercise_service.count_exercises(
                db=db,
                telegram_id=telegram_id,
                start_date=month_start,
                end_date=today
            )
            total = counts[0].count if counts else 0

            await update.message.reply_text(
                f"✅ Entrenamiento registrado para {today}\n\n"
                f"Descripción: {description}\n"
                f"Total de entrenamientos este mes: {total}"
            )
        except ValueError as e:
            await update.message.reply_text(
                f"❌ Error: {str(e)}\n\n"
                "Primero usa /start para registrarte."
            )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - Show stats for current month"""
    telegram_id = update.effective_user.id
    chat_type = update.effective_chat.type
    today = date.today()
    month_start = today.replace(day=1)

    async with AsyncSessionLocal() as db:
        # Detectar si es un grupo
        if chat_type in ["group", "supergroup"]:
            # En grupos: mostrar stats de todos los usuarios
            # Obtener todos los ejercicios del grupo en el mes
            all_exercises = await exercise_service.get_exercises_by_date_range(
                db=db,
                start_date=month_start,
                end_date=today
            )

            # Agrupar por usuario
            user_stats = {}
            for exercise in all_exercises:
                user_id = exercise.user_id
                if user_id not in user_stats:
                    user = await user_service.get_user_by_id(db, user_id)
                    user_stats[user_id] = {
                        "user": user,
                        "count": 0
                    }
                user_stats[user_id]["count"] += 1

            # Formatear mensaje para grupo
            month_name = today.strftime("%B %Y")
            message = f"📊 Estadísticas del Grupo - {month_name}\n\n"

            if user_stats:
                for user_id, stats in sorted(user_stats.items(), key=lambda x: x[1]["count"], reverse=True):
                    user = stats["user"]
                    count = stats["count"]
                    name = user.first_name or user.username or f"User {user_id}"
                    message += f"• {name}: {count} días\n"
            else:
                message += "No hay entrenamientos registrados este mes."

            message += "\n\n¡Sigan así! 💪"

        else:
            # Chat privado: mostrar stats personales (código existente)
            counts = await exercise_service.count_exercises(
                db=db,
                telegram_id=telegram_id,
                start_date=month_start,
                end_date=today
            )

            total = counts[0].count if counts else 0

            # Get recent exercises
            recent_exercises = await exercise_service.get_recent_exercises(
                db=db,
                telegram_id=telegram_id,
                limit=5
            )

            # Format message
            month_name = today.strftime("%B %Y")
            message = f"📊 Tus Estadísticas - {month_name}\n\n"
            message += f"Total de entrenamientos: {total} días\n\n"

            if recent_exercises:
                message += "Últimos entrenamientos:\n"
                message += format_exercise_list(recent_exercises)
            else:
                message += "No hay entrenamientos registrados este mes."

            message += "\n\n¡Sigue así! 💪"

        await update.message.reply_text(message)


async def stats_month_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats_month command - Show stats for specific month"""
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "❌ Formato incorrecto.\n\n"
            "Uso: /stats_month <YYYY-MM>\n"
            "Ejemplo: /stats_month 2025-12"
        )
        return

    month_str = context.args[0]
    date_range = parse_month(month_str)

    if not date_range:
        await update.message.reply_text(
            "❌ Formato de mes inválido.\n\n"
            "Usa el formato YYYY-MM\n"
            "Ejemplo: 2025-12"
        )
        return

    start_date, end_date = date_range
    telegram_id = update.effective_user.id

    async with AsyncSessionLocal() as db:
        # Get count
        counts = await exercise_service.count_exercises(
            db=db,
            telegram_id=telegram_id,
            start_date=start_date,
            end_date=end_date
        )

        total = counts[0].count if counts else 0

        # Format message
        month_name = start_date.strftime("%B %Y")
        message = f"📊 Tus Estadísticas - {month_name}\n\n"
        message += f"Total de entrenamientos: {total} días\n\n"
        message += f"Período: {start_date} a {end_date}"

        await update.message.reply_text(message)


async def stats_custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats_custom command - Show stats for custom date range"""
    if not context.args or len(context.args) != 2:
        await update.message.reply_text(
            "❌ Formato incorrecto.\n\n"
            "Uso: /stats_custom <fecha-inicio> <fecha-fin>\n"
            "Ejemplo: /stats_custom 2026-01-01 2026-01-15"
        )
        return

    start_date_str = context.args[0]
    end_date_str = context.args[1]

    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)

    if not start_date or not end_date:
        await update.message.reply_text(
            "❌ Formato de fecha inválido.\n\n"
            "Usa el formato YYYY-MM-DD\n"
            "Ejemplo: 2026-01-15"
        )
        return

    if start_date > end_date:
        await update.message.reply_text(
            "❌ La fecha de inicio debe ser anterior a la fecha de fin."
        )
        return

    telegram_id = update.effective_user.id

    async with AsyncSessionLocal() as db:
        # Get count
        counts = await exercise_service.count_exercises(
            db=db,
            telegram_id=telegram_id,
            start_date=start_date,
            end_date=end_date
        )

        total = counts[0].count if counts else 0

        # Format message
        message = f"📊 Tus Estadísticas\n\n"
        message += f"Total de entrenamientos: {total} días\n\n"
        message += f"Período: {start_date} a {end_date}"

        await update.message.reply_text(message)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Exception while handling an update: {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Lo siento, ocurrió un error. Por favor, intenta de nuevo más tarde."
        )

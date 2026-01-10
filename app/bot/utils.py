from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def parse_date(date_str: str) -> date | None:
    """Parse date string in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_month(month_str: str) -> tuple[date, date] | None:
    """Parse month string in YYYY-MM format and return start and end dates"""
    try:
        month_date = datetime.strptime(month_str, "%Y-%m")
        start_date = month_date.date()
        # Get last day of month
        next_month = month_date + relativedelta(months=1)
        end_date = next_month.date() - relativedelta(days=1)
        return start_date, end_date
    except ValueError:
        return None


def format_exercise_list(exercises) -> str:
    """Format list of exercises for display"""
    if not exercises:
        return "No hay entrenamientos registrados."

    lines = []
    for exercise in exercises:
        lines.append(f"• {exercise.day}: {exercise.description}")

    return "\n".join(lines)

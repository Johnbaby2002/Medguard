from datetime import date, datetime, time, timedelta

from app.models import MedicationLog, Reminder, ReminderStatus


def scheduled_datetime(day: date, reminder_time: str) -> datetime:
    hour, minute = (int(part) for part in reminder_time.split(":"))
    return datetime.combine(day, time(hour=hour, minute=minute))


def logs_for_day(logs: list[MedicationLog], day: date) -> list[MedicationLog]:
    return [log for log in logs if log.logged_at.date() == day]


def latest_log_for_reminder(reminder: Reminder, day: date) -> MedicationLog | None:
    logs = logs_for_day(list(reminder.logs), day)
    if not logs:
        return None
    return sorted(logs, key=lambda log: log.logged_at, reverse=True)[0]


def status_for_reminder(reminder: Reminder, day: date | None = None, now: datetime | None = None) -> ReminderStatus:
    day = day or date.today()
    now = now or datetime.now()
    latest = latest_log_for_reminder(reminder, day)
    if latest:
        return latest.status
    return ReminderStatus.missed if scheduled_datetime(day, reminder.time) < now else ReminderStatus.pending


def adherence_from_reminders(reminders: list[Reminder], days: int = 7) -> dict:
    today = date.today()
    trend = []
    total = taken = missed = late = 0
    for offset in range(days - 1, -1, -1):
        day = today - timedelta(days=offset)
        day_total = day_taken = day_missed = day_late = 0
        for reminder in reminders:
            status = status_for_reminder(reminder, day)
            day_total += 1
            if status == ReminderStatus.taken:
                day_taken += 1
            elif status == ReminderStatus.late:
                day_late += 1
            elif status == ReminderStatus.missed:
                day_missed += 1
        total += day_total
        taken += day_taken
        missed += day_missed
        late += day_late
        completed = day_taken + day_late
        trend.append(
            {
                "date": day.isoformat(),
                "scheduled": day_total,
                "taken": day_taken,
                "late": day_late,
                "missed": day_missed,
                "adherence_percentage": round((completed / day_total) * 100, 2) if day_total else None,
            }
        )
    completed_total = taken + late
    return {
        "total_scheduled_doses": total,
        "taken_doses": taken,
        "missed_doses": missed,
        "late_doses": late,
        "adherence_percentage": round((completed_total / total) * 100, 2) if total else None,
        "weekly_trend": trend,
    }

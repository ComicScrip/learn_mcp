"""Statistiques des tâches, regroupées par jour (semaine) ou par semaine (mois).

Règle de calcul : une tâche est comptée dans la période où elle a été CRÉÉE,
puis classée « effectuée » ou « à faire » selon son état actuel.
"""

from datetime import date, datetime, time, timedelta
from typing import Literal

from django.utils import timezone

from .models import Todo

Period = Literal["week", "month"]

DAYS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
MONTHS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def _monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _add_months(d: date, months: int) -> date:
    """1er du mois décalé de `months` mois."""
    index = d.year * 12 + d.month - 1 + months
    return date(index // 12, index % 12 + 1, 1)


def _buckets(period: Period, offset: int) -> tuple[str, list[tuple[str, date, date]]]:
    """Titre de la période + liste de (libellé, premier jour, dernier jour)."""
    today = timezone.localdate()

    if period == "week":
        monday = _monday(today) + timedelta(weeks=offset)
        days = [monday + timedelta(days=i) for i in range(7)]
        title = f"Semaine du {monday.day} {MONTHS[monday.month - 1]} {monday.year}"
        return title, [(f"{DAYS[d.weekday()]} {d.day}", d, d) for d in days]

    first = _add_months(today, offset)
    last = _add_months(first, 1) - timedelta(days=1)
    title = f"{MONTHS[first.month - 1].capitalize()} {first.year}"
    buckets = []
    start = first
    while start <= last:
        # Une barre par semaine (lundi -> dimanche), coupée aux bords du mois.
        end = min(_monday(start) + timedelta(days=6), last)
        buckets.append((f"{start.day}–{end.day}", start, end))
        start = end + timedelta(days=1)
    return title, buckets


def todo_stats(period: Period = "week", offset: int = 0) -> dict:
    title, buckets = _buckets(period, offset)

    tz = timezone.get_current_timezone()
    range_start = datetime.combine(buckets[0][1], time.min, tz)
    range_end = datetime.combine(buckets[-1][2] + timedelta(days=1), time.min, tz)
    todos = Todo.objects.filter(created_at__gte=range_start, created_at__lt=range_end)

    rows = [{"label": label, "done": 0, "pending": 0} for label, _, _ in buckets]
    for todo in todos:
        day = timezone.localtime(todo.created_at).date()
        for row, (_, start, end) in zip(rows, buckets):
            if start <= day <= end:
                row["done" if todo.done else "pending"] += 1
                break

    done = sum(r["done"] for r in rows)
    pending = sum(r["pending"] for r in rows)
    return {
        "period": period,
        "offset": offset,
        "title": title,
        "buckets": rows,
        "totals": {"done": done, "pending": pending},
    }

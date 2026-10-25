"""Remplit la base avec ~10 semaines de tâches factices.

    python manage.py seed_todos

⚠️ Supprime d'abord toutes les tâches existantes.
"""

import random
from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from todos.models import Todo

TITLES = [
    "Répondre aux emails", "Relire la PR de Léa", "Faire les courses",
    "Préparer la réunion d'équipe", "Appeler le plombier", "Sport : 30 min de course",
    "Mettre à jour le README", "Payer les factures", "Lire un chapitre",
    "Corriger le bug d'affichage", "Écrire les tests", "Ranger le bureau",
    "Planifier la semaine", "Déployer en staging", "Réserver le restaurant",
]


class Command(BaseCommand):
    help = "Supprime les tâches et crée des données factices sur ~10 semaines."

    def handle(self, *args, **options):
        rng = random.Random(42)  # même graine -> mêmes données à chaque fois
        now = timezone.now()
        today = timezone.localdate()
        tz = timezone.get_current_timezone()

        Todo.objects.all().delete()
        todos = []
        for days_ago in range(70, -1, -1):
            day = today - timedelta(days=days_ago)
            # Moins de tâches le week-end.
            count = rng.randint(0, 3) if day.weekday() >= 5 else rng.randint(2, 7)
            # Plus une tâche est ancienne, plus elle a de chances d'être faite.
            done_chance = 0.4 if days_ago == 0 else min(0.95, 0.6 + days_ago * 0.03)

            for _ in range(count):
                created = datetime.combine(day, time(rng.randint(8, 19), rng.randint(0, 59)), tz)
                if created > now:
                    created = now - timedelta(minutes=rng.randint(1, 60))
                done = rng.random() < done_chance
                done_at = min(created + timedelta(hours=rng.randint(1, 48)), now) if done else None
                todos.append(
                    Todo(title=rng.choice(TITLES), done=done, created_at=created, done_at=done_at)
                )

        Todo.objects.bulk_create(todos)
        self.stdout.write(self.style.SUCCESS(f"{len(todos)} tâches factices créées."))

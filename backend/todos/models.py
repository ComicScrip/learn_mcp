from django.db import models
from django.utils import timezone


class Todo(models.Model):
    title = models.CharField(max_length=200)
    done = models.BooleanField(default=False)
    # Historique : quand la tâche a été créée, et quand elle a été terminée.
    # (default=timezone.now plutôt que auto_now_add, pour que les données
    #  factices puissent être datées dans le passé.)
    created_at = models.DateTimeField(default=timezone.now)
    done_at = models.DateTimeField(null=True, blank=True)

    def set_done(self, done: bool):
        self.done = done
        self.done_at = timezone.now() if done else None

    def __str__(self):
        return self.title

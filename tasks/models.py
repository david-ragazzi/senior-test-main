from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class TaskStatus(models.TextChoices):
    TODO = "TODO", _("To Do")
    IN_PROGRESS = "IN_PROGRESS", _("In Progress")
    DONE = "DONE", _("Done")


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=12, choices=TaskStatus.choices, default=TaskStatus.IN_PROGRESS)
    priority = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

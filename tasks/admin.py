from django.contrib import admin
from .models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "priority", "status", "created_at")
    list_filter = ("status", "priority")
    ordering = ("created_at",)
    search_fields = ("title", "description",)


admin.site.register(Task, TaskAdmin)

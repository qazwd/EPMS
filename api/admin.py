from django.contrib import admin

# Register your models here.

from .models import UsersInfo, Projects, ProjectPhases, Reports, Logs, LogsDate


admin.site.register(UsersInfo)
admin.site.register(Projects)
admin.site.register(ProjectPhases)
admin.site.register(Reports)
admin.site.register(Logs)
admin.site.register(LogsDate)

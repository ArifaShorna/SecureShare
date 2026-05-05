from django.contrib import admin
from .models import UploadedFile, ActivityLog, SharedFile

admin.site.register(UploadedFile)
admin.site.register(ActivityLog)
admin.site.register(SharedFile)
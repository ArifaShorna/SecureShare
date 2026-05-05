from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    file_hash = models.CharField(max_length=64, blank=True, null=True)
    download_count = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    file_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"
class SharedFile(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_by')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_with')
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.file.name} shared with {self.shared_with.username}"
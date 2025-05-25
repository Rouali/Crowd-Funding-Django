from django.db import models
from django.conf import settings
from apps.projects.models import Project

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_reported = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"


# Create your models here.

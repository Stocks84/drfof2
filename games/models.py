from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Game(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    rules = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

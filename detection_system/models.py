# Create your models here.

from django.db import models
from django.db import models

class Message(models.Model):
    text = models.TextField()
    is_toxic = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]
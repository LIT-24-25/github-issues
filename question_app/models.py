from django.db import models

class Question(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    context = models.TextField()
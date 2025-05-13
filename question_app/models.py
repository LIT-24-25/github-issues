from django.db import models
from conversation.models import Conversation

class Question(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    context = models.TextField()
    model = models.TextField()
    conversation = models.ForeignKey(Conversation, related_name='questions', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.question
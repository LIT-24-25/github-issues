from django.shortcuts import render
from rest_framework import viewsets
from .models import Question
from .serializers import QuestionSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

def index(request):
    return render(request, 'question_app/index.html')
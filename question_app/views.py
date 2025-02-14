from django.shortcuts import render
from rest_framework import viewsets
from .models import Question
from .serializers import QuestionSerializer
from train import model_call

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

def question_ask(request):
    if request.method == "GET":
        return render(request, 'question_app/question_form.html')
    elif request.method == "POST":
        question = request.POST.get('question')
        model_response = model_call(question)
        Question.objects.create(question=question, answer=model_response)
        context = {
        'question': question,
        'answer': model_response
        }
        
        return render(request, 'question_app/question_response.html', context)
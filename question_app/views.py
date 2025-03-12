from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.views.generic import TemplateView
from .models import Question
from .serializers import QuestionSerializer
from question_app.instances import my_model, my_chroma

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    renderer_classes = [JSONRenderer]

    def list(self, request):
        """Get all questions"""
        questions = self.get_queryset().order_by('-id')  # Most recent first
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new question and get model response"""
        question_text = request.data.get('question')
        request_model = request.data.get('model')
        
        if not question_text:
            return Response(
                {'error': 'Question is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if request_model == 'GigaChat':
                context, model_response = my_model.call_gigachat(question_text, my_chroma)
            else:
                context, model_response = my_model.call_qwen(question_text, my_chroma)
                
            question = Question.objects.create(
                question=question_text,
                answer=model_response,
                context=context
            )
            serializer = self.get_serializer(question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['GET'])
    def view_response(self, request, pk=None):
        """View a specific question response"""
        question = self.get_object()
        return Response({
            'id': question.id,
            'question': question.question,
            'answer': question.answer,
            'context': question.context
        })

class QuestionFormView(TemplateView):
    """Serve the main Vue.js application template"""
    template_name = "question_app/question.html"
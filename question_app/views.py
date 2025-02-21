from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from .models import Question
from .serializers import QuestionSerializer
from business_logic.train import model_call

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    @action(detail=False, methods=['GET'], renderer_classes=[TemplateHTMLRenderer])
    def ask_form(self, request):
        """Render the question form"""
        return Response(
            template_name='question_app/question_form.html'
        )

    @action(detail=True, methods=['GET'], renderer_classes=[TemplateHTMLRenderer])
    def view_response(self, request, pk=None):
        """View a specific question response"""
        question = self.get_object()
        return Response(
            {
                'question': question.question,
                'answer': question.answer,
                'context': question.context
            },
            template_name='question_app/question_response.html'
        )

    def create(self, request, *args, **kwargs):
        """Create a new question and get model response"""
        question_text = request.data.get('question')
        if not question_text:
            return Response(
                {'error': 'Question is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            context, model_response = model_call(question_text)
            question = Question.objects.create(
                question=question_text,
                answer=model_response,
                context=context
            )
            serializer = self.get_serializer(question)
            
            if request.accepted_renderer.format == 'html':
                return redirect('question-view-response', pk=question.pk)
            
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
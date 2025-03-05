from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from .models import Question
from .serializers import QuestionSerializer
from question_app.instances import my_model, my_chroma

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'question_app/question_form.html'

    @action(detail=False, methods=['GET'], renderer_classes=[TemplateHTMLRenderer])
    def ask_form(self, request):
        """Render the question form"""
        self.template_name = 'question_app/question_form.html'
        return Response({}, template_name=self.template_name)

    @action(detail=True, methods=['GET'], renderer_classes=[TemplateHTMLRenderer])
    def view_response(self, request, pk=None):
        """View a specific question response"""
        question = self.get_object()
        
        if request.accepted_renderer.format == 'html':
            return Response(
                {
                    'question': question.question,
                    'answer': question.answer,
                    'context': question.context
                },
                template_name='question_app/question_response.html'
            )
        
        # For API requests
        return Response({
            'question': question.question,
            'answer': question.answer,
            'context': question.context
        })

    def create(self, request, *args, **kwargs):
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
            
            if request.accepted_renderer.format == 'html':
                return redirect('question-view-response', pk=question.pk)
            
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e), 'retrived':question_text}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
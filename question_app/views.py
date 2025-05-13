from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.views import APIView
from django.views.generic import TemplateView
from .models import Question
from .serializers import QuestionSerializer
from question_app.instances import my_model, my_chroma, training_metadata
from conversation.models import Conversation
from gigachat.models import Messages, MessagesRole

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    renderer_classes = [JSONRenderer]

    def list(self, request):
        """Get all questions"""
        conversation_id = request.query_params.get('conversation')
        
        if conversation_id:
            questions = self.get_queryset().filter(conversation_id=conversation_id).order_by('id')
        else:
            questions = self.get_queryset().order_by('-id')  # Most recent first
            
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new question and get model response"""
        question_text = request.data.get('question')
        request_model = request.data.get('model')
        conversation_id = request.data.get('conversation_id')
        
        if not question_text:
            return Response(
                {'error': 'Question is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get or create a conversation
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    # We're continuing an existing conversation, so don't update the title
                except Conversation.DoesNotExist:
                    return Response(
                        {'error': 'Conversation not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Create a new conversation with a truncated title (4-5 words)
                words = question_text.split()
                short_title = ' '.join(words[:5]) if len(words) > 5 else question_text
                
                # Limit the title length for DB field size
                if len(short_title) > 255:
                    short_title = short_title[:252] + '...'
                
                conversation = Conversation.objects.create(
                    title=short_title
                )
            
            # Get message history for this conversation if continuing a conversation
            message_history = []
            if conversation_id:
                previous_questions = Question.objects.filter(conversation_id=conversation_id).order_by('id')
                if request_model == 'OpenRouter':
                    for q in previous_questions:
                        message_history.append({
                            "role": "user",
                            "content": q.question
                        })
                        message_history.append({
                            "role": "assistant",
                            "content": q.answer
                        })
                elif request_model == 'GigaChat':
                    for q in previous_questions:
                        message_history.append(
                            Messages(
                                role=MessagesRole.USER,
                                content=q.question
                            )
                        )
                        message_history.append(
                            Messages(
                                role=MessagesRole.ASSISTANT,
                                content=q.answer
                            )
                        )
            
            # Call the appropriate model
            if request_model == 'OpenRouter':
                urls, model_response, model_name = my_model.call_openrouter(question_text, my_chroma, message_history)
            elif request_model == 'GigaChat':
                urls, model_response = my_model.call_gigachat(question_text, my_chroma, message_history)
                model_name = "GigaChat"
            else:
                urls, model_response, model_name = "None", "None", "None"
                
            question = Question.objects.create(
                question=question_text,
                answer=model_response,
                context=urls,
                model=model_name,
                conversation=conversation
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
            'context': question.context,
            'model': question.model,
            'conversation_id': question.conversation_id
        })

class QuestionFormView(TemplateView):
    """Serve the main Vue.js application template"""
    template_name = "question_app/question.html"


class TrainingStatsView(APIView):
    """API endpoint to retrieve training metadata"""
    
    def get(self, request):
        """Return the training metadata"""
        return Response(training_metadata)

# Add a new view to get all conversations
class ConversationViewSet(viewsets.ViewSet):
    """API endpoint to retrieve conversations"""
    
    def list(self, request):
        """Return all conversations with their latest question"""
        conversations = Conversation.objects.all().order_by('-updated_at')
        result = []
        
        for conv in conversations:
            latest_question = Question.objects.filter(conversation=conv).order_by('-id').first()
            if latest_question:
                result.append({
                    'id': conv.id,
                    'title': conv.title,  # Use the original title as stored in the database
                    'created_at': conv.created_at,
                    'updated_at': conv.updated_at,
                    'latest_question': {
                        'id': latest_question.id,
                        'question': latest_question.question,
                        'model': latest_question.model
                    }
                })
        
        return Response(result)
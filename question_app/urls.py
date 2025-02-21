from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('', QuestionViewSet.as_view({
        'get': 'ask_form',
        'post': 'create'
    }), name='ask-form'),  # Changed from 'root' to 'ask-form'
    path('api/', include(router.urls)),
]
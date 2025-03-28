from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, QuestionFormView, TrainingStatsView

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('', QuestionFormView.as_view(), name='ask-form'),
    path('api/', include(router.urls)),
    path('api/training-stats/', TrainingStatsView.as_view(), name='training-stats'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, QuestionFormView

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('', QuestionFormView.as_view(), name='ask-form'),
    path('api/', include(router.urls)),
]
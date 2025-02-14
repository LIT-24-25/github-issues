from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_ask, name='question_form'),
    path('question-response/', views.question_ask, name='question_response'),
]
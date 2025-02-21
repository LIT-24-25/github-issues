from django.apps import AppConfig


class QuestionAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'question_app'
    
    def ready(self):
        # Import initialization module when Django starts
        from . import initialize
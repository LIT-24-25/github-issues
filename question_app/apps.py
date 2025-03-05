from django.apps import AppConfig


class QuestionAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'question_app'
    
    def ready(self):
        from question_app.instances import initialize_instances
        initialize_instances()
        from question_app.instances import my_model, my_chroma
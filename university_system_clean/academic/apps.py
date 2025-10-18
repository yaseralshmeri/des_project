from django.apps import AppConfig


class AcademicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academic'
    verbose_name = 'Academic Management'

    def ready(self):
        import academic.signals
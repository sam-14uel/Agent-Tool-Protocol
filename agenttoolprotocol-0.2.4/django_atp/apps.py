from django.apps import AppConfig


class DjangoAtpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_atp"
    verbose_name = "Django ATP"
    label = "django_atp"

    def ready(self):
        # No singleton, just ensure registry exists
        from . import registry
        registry.init_registry()

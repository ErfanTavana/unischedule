from django.apps import AppConfig


class InstitutionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'institutions'

    def ready(self) -> None:
        """Import signal handlers when the app is ready."""

        # Import ensures the pre_save hook for slug normalization is registered.
        from . import signals  # noqa: F401

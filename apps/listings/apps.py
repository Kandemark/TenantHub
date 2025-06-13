from django.apps import AppConfig


class ListingsConfig(AppConfig):
    """
    AppConfig for the Listings app.
    Handles app-specific configuration and initialization.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.listings'
    verbose_name = "Listings"

    def ready(self):
        """
        Import signals and perform app-specific initialization.
        """
        # Import signals to ensure they are registered
        try:
            import apps.listings.signals  # noqa: F401
        except ImportError:
            pass
        # ...add any other startup logic here...

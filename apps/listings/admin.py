from django.contrib import admin
from . import models

# Automatically register all models in the app
for model in admin.site._registry.copy():
    if model._meta.app_label == 'listings':
        admin.site.unregister(model)

for model_name in dir(models):
    model = getattr(models, model_name)
    if hasattr(model, '_meta') and getattr(model._meta, 'app_label', None) == 'listings':
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass

# Example: Custom admin classes for common models (customize as needed)
if hasattr(models, 'Listing'):
    class ListingAdmin(admin.ModelAdmin):
        list_display = [field.name for field in models.Listing._meta.fields]
        search_fields = [field.name for field in models.Listing._meta.fields if field.get_internal_type() in ['CharField', 'TextField']]
        list_filter = [field.name for field in models.Listing._meta.fields if field.get_internal_type() in ['BooleanField', 'DateField', 'DateTimeField', 'ForeignKey']]
        ordering = ['-id']

    admin.site.unregister(models.Listing)
    admin.site.register(models.Listing, ListingAdmin)

# ...add similar custom admin classes for other models as needed...

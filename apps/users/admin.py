from django.contrib import admin
from . import models

# Automatically register all models in the users app
for model in admin.site._registry.copy():
    if model._meta.app_label == 'users':
        admin.site.unregister(model)

for model_name in dir(models):
    model = getattr(models, model_name)
    if hasattr(model, '_meta') and getattr(model._meta, 'app_label', None) == 'users':
        try:
            class GenericAdmin(admin.ModelAdmin):
                list_display = [field.name for field in model._meta.fields]
                search_fields = [field.name for field in model._meta.fields if field.get_internal_type() in ['CharField', 'EmailField']]
                list_filter = [field.name for field in model._meta.fields if field.get_internal_type() in ['BooleanField', 'NullBooleanField', 'DateField', 'DateTimeField']]
            admin.site.register(model, GenericAdmin)
        except admin.sites.AlreadyRegistered:
            pass

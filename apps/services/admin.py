from django.contrib import admin
from . import models

# Automatically register all models in the app
for model in admin.site._registry.copy():
    if model.__module__ == models.__name__:
        admin.site.unregister(model)

for attr_name in dir(models):
    attr = getattr(models, attr_name)
    if hasattr(attr, "_meta") and getattr(attr._meta, "abstract", False) is False:
        try:
            class GenericAdmin(admin.ModelAdmin):
                list_display = [field.name for field in attr._meta.fields]
                search_fields = [field.name for field in attr._meta.fields if field.get_internal_type() in ("CharField", "TextField")]
                list_filter = [field.name for field in attr._meta.fields if field.get_internal_type() in ("BooleanField", "NullBooleanField", "DateField", "DateTimeField", "ForeignKey")]
            admin.site.register(attr, GenericAdmin)
        except admin.sites.AlreadyRegistered:
            pass

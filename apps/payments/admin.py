from django.contrib import admin
from . import models

# Automatically register all models in the payments app
for model in admin.site.apps.get_app_config('payments').get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

# Example: Custom admin classes for common payment-related models
# Uncomment and adjust as needed if these models exist in your app

# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'amount', 'status', 'created_at')
#     list_filter = ('status', 'created_at')
#     search_fields = ('user__username', 'user__email', 'id')
#     date_hierarchy = 'created_at'
#
# class InvoiceAdmin(admin.ModelAdmin):
#     list_display = ('id', 'tenant', 'amount_due', 'due_date', 'paid')
#     list_filter = ('paid', 'due_date')
#     search_fields = ('tenant__username', 'tenant__email', 'id')
#     date_hierarchy = 'due_date'
#
# # Register with custom admin if you have such models
# # admin.site.unregister(models.Payment)
# # admin.site.register(models.Payment, PaymentAdmin)
# # admin.site.unregister(models.Invoice)
# # admin.site.register(models.Invoice, InvoiceAdmin)

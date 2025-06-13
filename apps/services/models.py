from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

class ServiceQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, deleted=False)

    def deleted(self):
        return self.filter(deleted=True)

    def all_with_deleted(self):
        return self.all()

class ServiceManager(models.Manager):
    def get_queryset(self):
        return ServiceQuerySet(self.model, using=self._db).filter(deleted=False)

    def all_with_deleted(self):
        return ServiceQuerySet(self.model, using=self._db).all()

    def deleted(self):
        return ServiceQuerySet(self.model, using=self._db).filter(deleted=True)

class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    objects = ServiceManager()
    all_objects = models.Manager()  # includes deleted

    class Meta:
        ordering = ['name']
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.deleted = True
        self.save(update_fields=['deleted', 'updated_at'])

    def restore(self):
        self.deleted = False
        self.save(update_fields=['deleted', 'updated_at'])

    def activate(self):
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    @property
    def is_deleted(self):
        return self.deleted

# Example of a related model (optional, for demonstration)
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    services = models.ManyToManyField(Service, related_name='categories', blank=True)

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name

# Signals for logging or additional logic
@receiver(pre_save, sender=Service)
def pre_save_service(sender, instance, **kwargs):
    # Example: log or modify instance before saving
    pass

@receiver(post_save, sender=Service)
def post_save_service(sender, instance, created, **kwargs):
    # Example: log or trigger actions after saving
    pass

# ...existing code...

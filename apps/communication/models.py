from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Thread(models.Model):
    """
    Represents a conversation between two or more users.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='threads')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Thread"
        verbose_name_plural = "Threads"

    def __str__(self):
        return f"Thread {self.id} ({self.participants.count()} participants)"

    def last_message(self):
        return self.messages.order_by('-sent_at').first()

    def unread_messages_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def add_participant(self, user):
        self.participants.add(user)

    def remove_participant(self, user):
        self.participants.remove(user)

    def has_participant(self, user):
        return self.participants.filter(pk=user.pk).exists()

class Message(models.Model):
    """
    Represents a message sent in a thread.
    """
    thread = models.ForeignKey(
        Thread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message {self.id} from {self.sender} in Thread {self.thread.id}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def mark_as_unread(self):
        if self.is_read:
            self.is_read = False
            self.save(update_fields=['is_read'])

    def soft_delete(self):
        if not self.is_deleted:
            self.is_deleted = True
            self.save(update_fields=['is_deleted'])

    def restore(self):
        if self.is_deleted:
            self.is_deleted = False
            self.save(update_fields=['is_deleted'])

class Attachment(models.Model):
    """
    Represents a file attached to a message.
    """
    message = models.ForeignKey(
        Message, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    def __str__(self):
        return f"Attachment {self.id} for Message {self.message.id}"

    def filename(self):
        return self.file.name.split('/')[-1]

# Signals for notifications or other side effects
@receiver(post_save, sender=Message)
def notify_new_message(sender, instance, created, **kwargs):
    if created:
        # Placeholder for notification logic
        # e.g., send notification to thread participants except sender
        pass

from django.db import models
from django.core.cache import cache

class SystemSettings(models.Model):
    """Singleton model to store global system configuration."""
    active_tax_year = models.PositiveIntegerField(
        default=2026,
        help_text="The current active tax year. Change this to update the entire platform's context."
    )

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.set('system_settings', self)

    @classmethod
    def load(cls):
        obj = cache.get('system_settings')
        if not obj:
            obj, created = cls.objects.get_or_create(pk=1)
            cache.set('system_settings', obj)
        return obj

    def __str__(self):
        return f"System Settings (Active Year: {self.active_tax_year})"

class SystemErrorLog(models.Model):
    """Stores unhandled exceptions for support team to review."""
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    exception_type = models.CharField(max_length=255)
    exception_message = models.TextField()
    traceback = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "System Error"
        verbose_name_plural = "System Errors"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.exception_type} at {self.path}"

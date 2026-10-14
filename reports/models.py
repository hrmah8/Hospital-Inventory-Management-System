from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class InventoryReports(models.Model):
    title = models.CharField(max_length=255)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    summary_data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.title} ({self.generated_at.strftime('%Y-%m-%d')})"
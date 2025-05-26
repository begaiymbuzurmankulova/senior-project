from django.db import models
from django.conf import settings
from apartments.models import Apartment

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'apartment')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} favorited {self.apartment}"

from django.db import models
from django.conf import settings
from apartments.models import Apartment
from bookings.models import Booking

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.reviewer.email} for {self.apartment.title}"

    class Meta:
        ordering = ['-created_at']


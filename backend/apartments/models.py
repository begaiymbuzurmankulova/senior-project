from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class PropertyType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class name")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Property Type"
        verbose_name_plural = "Property Types"

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, null=True, blank=True, help_text="Bootstrap icon class name")
    apartments = models.ManyToManyField('Apartment', related_name='amenities')

    class Meta:
        verbose_name_plural = "amenities"
        ordering = ['name']

    def __str__(self):
        return self.name

class Apartment(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_apartments'
    )
    property_type = models.ForeignKey(
        'PropertyType',
        on_delete=models.PROTECT,
        related_name='properties'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    price_per_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Cost per month for long-term rentals."
    )
    price_per_night = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0.00,
        help_text="Cost per night for short-term stays."
    )

    bedrooms = models.IntegerField(validators=[MinValueValidator(0)])
    bathrooms = models.IntegerField(validators=[MinValueValidator(0)])
    size_sqm = models.IntegerField(validators=[MinValueValidator(0)])

    max_guests = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Maximum number of guests allowed."
    )

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Extra stats for analytics & sorting
    average_rating = models.FloatField(null=True, blank=True)
    bookings_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['price_per_month']),
            models.Index(fields=['is_available']),
            models.Index(fields=['property_type']),
        ]

    def __str__(self):
        return self.title

    def get_primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def price_range(self):
        return {
            'min': self.price_per_night,
            'max': self.price_per_month
        }

    @property
    def popularity_score(self):
        return (
            self.bookings_count + self.favorites_count + self.views_count
        )

        

class ApartmentImage(models.Model):
    apartment = models.ForeignKey(
        Apartment, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='apartments/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['is_primary']),
        ]

    def __str__(self):
        return f"Image for {self.apartment.title}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set all other images of this apartment to not primary
            ApartmentImage.objects.filter(
                apartment=self.apartment,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

class ApartmentAvailability(models.Model):
    """Model to track specific availability periods"""
    apartment = models.ForeignKey(
        Apartment, 
        on_delete=models.CASCADE, 
        related_name='availability_periods'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_available = models.BooleanField(default=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = "Apartment Availability"
        verbose_name_plural = "Apartment Availabilities"
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.apartment.title} - {status} ({self.start_date} to {self.end_date})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date")
        
        # Check for overlapping periods
        overlapping = ApartmentAvailability.objects.filter(
            apartment=self.apartment,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exclude(id=self.id)
        
        if overlapping.exists():
            raise ValidationError("This period overlaps with an existing availability period")


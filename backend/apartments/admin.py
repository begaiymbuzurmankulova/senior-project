from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg
from .models import Apartment, ApartmentImage, Amenity

class ApartmentImageInline(admin.TabularInline):
    model = ApartmentImage
    extra = 1
    fields = ('image', 'is_primary', 'preview_image')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="150" height="150" />',
                obj.image.url
            )
        return "No image"

class PriceRangeFilter(admin.SimpleListFilter):
    title = 'price range'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('0-500', '0-500'),
            ('501-1000', '501-1000'),
            ('1001-2000', '1001-2000'),
            ('2001+', '2001+'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0-500':
            return queryset.filter(price_per_month__lte=500)
        if self.value() == '501-1000':
            return queryset.filter(price_per_month__gt=500, price_per_month__lte=1000)
        if self.value() == '1001-2000':
            return queryset.filter(price_per_month__gt=1000, price_per_month__lte=2000)
        if self.value() == '2001+':
            return queryset.filter(price_per_month__gt=2000)

@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'owner', 
        'city', 
        'price_per_month', 
        'bedrooms', 
        'is_available',
        'average_rating',
        'booking_count'
    )
    list_filter = (
        'is_available', 
        'city', 
        'bedrooms',
        PriceRangeFilter
    )
    search_fields = ('title', 'description', 'address', 'owner__email')
    inlines = [ApartmentImageInline]
    actions = ['mark_as_available', 'mark_as_unavailable']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'owner', 'description')
        }),
        ('Location', {
            'fields': ('address', 'city', 'country')
        }),
        ('Details', {
            'fields': ('price_per_month', 'bedrooms', 'bathrooms', 'size_sqm')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
    )

    def average_rating(self, obj):
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        if avg:
            return round(avg, 2)
        return 'No ratings'
    average_rating.short_description = 'Avg Rating'

    def booking_count(self, obj):
        return obj.bookings.count()
    booking_count.short_description = 'Bookings'

    def mark_as_available(self, request, queryset):
        queryset.update(is_available=True)
    mark_as_available.short_description = "Mark selected apartments as available"

    def mark_as_unavailable(self, request, queryset):
        queryset.update(is_available=False)
    mark_as_unavailable.short_description = "Mark selected apartments as unavailable"

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'apartments_count')
    search_fields = ('name',)

    def apartments_count(self, obj):
        return obj.apartments.count()
    apartments_count.short_description = 'Number of Apartments'


from django.contrib import admin
from django.utils.html import format_html
from datetime import date
from .models import Booking, BookingDocument

class BookingDocumentInline(admin.TabularInline):
    model = BookingDocument
    extra = 1
    fields = ('document', 'document_type', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

class BookingStatusFilter(admin.SimpleListFilter):
    title = 'booking status'
    parameter_name = 'status_type'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active Bookings'),
            ('past', 'Past Bookings'),
            ('future', 'Future Bookings'),
        )

    def queryset(self, request, queryset):
        today = date.today()
        if self.value() == 'active':
            return queryset.filter(start_date__lte=today, end_date__gte=today)
        if self.value() == 'past':
            return queryset.filter(end_date__lt=today)
        if self.value() == 'future':
            return queryset.filter(start_date__gt=today)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tenant',
        'apartment_link',
        'status',
        'start_date',
        'end_date',
        'total_price',
        'booking_duration',
        'has_review'
    )
    list_filter = (
        'status',
        BookingStatusFilter,
        'start_date',
        'end_date'
    )
    search_fields = (
        'tenant__email',
        'apartment__title',
        'id'
    )
    inlines = [BookingDocumentInline]
    actions = ['approve_bookings', 'reject_bookings', 'mark_as_completed']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('tenant', 'apartment', 'status')
        }),
        ('Dates and Price', {
            'fields': ('start_date', 'end_date', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def apartment_link(self, obj):
        return format_html(
            '<a href="/admin/apartments/apartment/{}/">{}</a>',
            obj.apartment.id,
            obj.apartment.title
        )
    apartment_link.short_description = 'Apartment'

    def booking_duration(self, obj):
        duration = (obj.end_date - obj.start_date).days
        return f"{duration} days"
    booking_duration.short_description = 'Duration'

    def has_review(self, obj):
        return hasattr(obj, 'review')
    has_review.boolean = True
    has_review.short_description = 'Reviewed'

    def approve_bookings(self, request, queryset):
        queryset.update(status='approved')
    approve_bookings.short_description = "Approve selected bookings"

    def reject_bookings(self, request, queryset):
        queryset.update(status='rejected')
    reject_bookings.short_description = "Reject selected bookings"

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected bookings as completed"


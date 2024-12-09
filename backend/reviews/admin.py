from django.contrib import admin
from django.utils.html import format_html
from .models import Review

class RatingFilter(admin.SimpleListFilter):
    title = 'rating category'
    parameter_name = 'rating_category'

    def lookups(self, request, model_admin):
        return (
            ('excellent', 'Excellent (5)'),
            ('good', 'Good (4)'),
            ('average', 'Average (3)'),
            ('poor', 'Poor (1-2)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'excellent':
            return queryset.filter(rating=5)
        if self.value() == 'good':
            return queryset.filter(rating=4)
        if self.value() == 'average':
            return queryset.filter(rating=3)
        if self.value() == 'poor':
            return queryset.filter(rating__lte=2)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'reviewer',
        'apartment_link',
        'rating_stars',
        'created_at',
        'comment_preview'
    )
    list_filter = (
        RatingFilter,
        'created_at',
    )
    search_fields = (
        'reviewer__email',
        'apartment__title',
        'comment'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('reviewer', 'apartment', 'booking')
        }),
        ('Review Content', {
            'fields': ('rating', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def apartment_link(self, obj):
        return format_html(
            '<a href="/admin/apartments/apartment/{}/">{}</a>',
            obj.apartment.id,
            obj.apartment.title
        )
    apartment_link.short_description = 'Apartment'

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: gold;">{}</span>',
            stars
        )
    rating_stars.short_description = 'Rating'

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment Preview'

    actions = ['mark_as_featured', 'hide_reviews']

    def mark_as_featured(self, request, queryset):
        # Add your featured logic here
        pass
    mark_as_featured.short_description = "Mark selected reviews as featured"

    def hide_reviews(self, request, queryset):
        # Add your hide logic here
        pass
    hide_reviews.short_description = "Hide selected reviews"


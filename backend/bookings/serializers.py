from rest_framework import serializers
from .models import Booking, BookingDocument
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from decimal import Decimal

class BookingDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDocument
        fields = ['id', 'document', 'document_type', 'uploaded_at']

class BookingDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDocument
        fields = ['document', 'document_type']

    def validate(self, data):
        if not data.get('document'):
            raise serializers.ValidationError("Document file is required.")
        if not data.get('document_type'):
            raise serializers.ValidationError("Document type is required.")
        return data



class BookingSerializer(serializers.ModelSerializer):
    documents = BookingDocumentSerializer(many=True, read_only=True)
    message = serializers.CharField(required=False, allow_blank=True)
    refund_amount = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'tenant', 'apartment', 'booking_type', 'start_date', 'end_date',
            'guest_count', 'status', 'payment_status', 'total_price',
            'message', 'approved_at', 'rejected_at', 'cancelled_at',
            'refund_status', 'refund_amount', 'refunded_at',
            'created_at', 'updated_at', 'documents'
        ]
        read_only_fields = [
            'tenant', 'status', 'payment_status', 'approved_at', 'rejected_at',
            'cancelled_at', 'created_at', 'updated_at', 'documents',
            'total_price', 'refund_status', 'refund_amount', 'refunded_at',
        ]

    def validate(self, data):
        apartment = data.get('apartment')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        guest_count = data.get('guest_count')

        if start_date >= end_date:
            raise serializers.ValidationError(_("Check-out must be after check-in."))

        if guest_count > apartment.max_guests:
            raise serializers.ValidationError(_(
                f"Guest count exceeds the apartment's maximum capacity of {apartment.max_guests}."
            ))

        overlapping = Booking.objects.filter(
            apartment=apartment,
            status__in=['approved', 'pending'],
            start_date__lt=end_date,
            end_date__gt=start_date
        )

        if self.instance:
            overlapping = overlapping.exclude(id=self.instance.id)

        if overlapping.exists():
            raise serializers.ValidationError(_("This apartment is not available for the selected dates."))

        return data

    def create(self, validated_data):
        apartment = validated_data['apartment']
        booking_type = validated_data.get('booking_type', 'night')
        nights = (validated_data['end_date'] - validated_data['start_date']).days

        if booking_type == 'night':
            validated_data['total_price'] = nights * apartment.price_per_night
        elif booking_type == 'month':
            months = max(1, nights // 30)  # charge per 30 days
            validated_data['total_price'] = months * apartment.price_per_month
        else:
            raise serializers.ValidationError("Invalid booking type.")

        return super().create(validated_data)

    def get_refund_amount(self, obj):
        # Placeholder logic for refunds
        return obj.total_price * Decimal("0.8") # Example: 80% refund

        


class BookingDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDocument
        fields = ['document', 'document_type']

    def validate(self, data):
        if not data.get('document'):
            raise serializers.ValidationError("Document file is required.")
        if not data.get('document_type'):
            raise serializers.ValidationError("Document type is required.")
        return data

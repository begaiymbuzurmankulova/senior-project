from rest_framework import serializers
from .models import LandlordReview
from reviews.models import Review
from apartments.models import Apartment
from bookings.models import Booking

class ReviewSerializer(serializers.ModelSerializer):
    apartment_id = serializers.IntegerField(write_only=True)
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all())

    class Meta:
        model = Review
        fields = [
            'id', 'apartment_id', 'booking', 'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        apartment_id = validated_data.pop('apartment_id')
        apartment = Apartment.objects.get(id=apartment_id)
        validated_data['apartment'] = apartment
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)

class LandlordReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandlordReview
        fields = ['id', 'tenant', 'booking', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # Automatically assign the current user as the reviewer
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)
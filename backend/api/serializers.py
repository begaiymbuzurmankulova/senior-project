from rest_framework import serializers
from django.contrib.auth import get_user_model
from apartments.models import Apartment, ApartmentImage, Amenity
from bookings.models import Booking, BookingDocument
from reviews.models import Review

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'profile_picture', 'bio')
        read_only_fields = ('id',)

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'

class ApartmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentImage
        fields = ('id', 'image', 'is_primary')

class ApartmentSerializer(serializers.ModelSerializer):
    images = ApartmentImageSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Apartment
        fields = '__all__'
        read_only_fields = ('owner',)

    def create(self, validated_data):
        request = self.context.get('request')
        apartment = Apartment.objects.create(owner=request.user, **validated_data)
        return apartment

class BookingDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDocument
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    documents = BookingDocumentSerializer(many=True, read_only=True)
    tenant = UserSerializer(read_only=True)
    apartment = ApartmentSerializer(read_only=True)
    apartment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('tenant', 'status', 'total_price')

    def create(self, validated_data):
        request = self.context.get('request')
        apartment_id = validated_data.pop('apartment_id')
        apartment = Apartment.objects.get(id=apartment_id)
        
        # Calculate total price
        days = (validated_data['end_date'] - validated_data['start_date']).days
        total_price = days * apartment.price_per_month / 30
        
        booking = Booking.objects.create(
            tenant=request.user,
            apartment=apartment,
            total_price=total_price,
            status='pending',
            **validated_data
        )
        return booking

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    apartment = ApartmentSerializer(read_only=True)
    apartment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('reviewer',)

    def create(self, validated_data):
        request = self.context.get('request')
        apartment_id = validated_data.pop('apartment_id')
        apartment = Apartment.objects.get(id=apartment_id)
        
        review = Review.objects.create(
            reviewer=request.user,
            apartment=apartment,
            **validated_data
        )
        return review


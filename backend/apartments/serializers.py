from rest_framework import serializers
from .models import Apartment, ApartmentImage, Amenity
from favorites.models import Favorite


class AmenitySerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(required=False)

    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon', 'distance']


class ApartmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentImage
        fields = ['id', 'image', 'is_primary']


class ApartmentSearchSerializer(serializers.ModelSerializer):
    images = ApartmentImageSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    annotated_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Apartment
        fields = [
            'id', 'title', 'description', 'address', 'city', 'country',
            'price_per_month', 'bedrooms', 'bathrooms', 'size_sqm',
            'is_available', 'images', 'amenities', 'primary_image',
            'annotated_rating', 'review_count', 'is_favorited'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ApartmentImageSerializer(primary_image).data
        return None

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, apartment=obj).exists()
        return False


class ApartmentDetailSerializer(serializers.ModelSerializer):
    images = ApartmentImageSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(source='annotated_rating', read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    owner_name = serializers.CharField(source='owner.first_name', read_only=True)
    owner_image = serializers.ImageField(source='owner.profile.image', read_only=True, allow_null=True)
    property_type = serializers.CharField(source='property_type.name', read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Apartment
        fields = [
            'id', 'title', 'description', 'address', 'city', 'country',
            'latitude', 'longitude',
            'price_per_month', 'bedrooms', 'bathrooms', 'size_sqm',
            'is_available', 'property_type',
            'images', 'primary_image', 'amenities',
            'average_rating', 'review_count',
            'owner_name', 'owner_image', 'is_favorited'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ApartmentImageSerializer(primary_image).data
        return None

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, apartment=obj).exists()
        return False
        
class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = '__all__'

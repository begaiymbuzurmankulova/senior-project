from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from datetime import datetime
from .models import Apartment
from bookings.models import Booking
from .serializers import ApartmentSearchSerializer
from math import radians, cos, sin, asin, sqrt


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


class PropertySearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        browse_all = request.GET.get('browse_all', 'false').lower() == 'true'

        location = request.GET.get('location')
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        guests = request.GET.get('guests', 1)

        try:
            guests = int(guests)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid guest count'}, status=status.HTTP_400_BAD_REQUEST)

        if not browse_all:
            if not location or not check_in or not check_out:
                return Response(
                    {'error': 'Missing required fields: check_in, check_out, and location are required unless browse_all=true'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Optional filters
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        property_type = request.GET.get('property_type')
        amenities = request.GET.get('amenities')
        bedrooms = request.GET.get('bedrooms')
        bathrooms = request.GET.get('bathrooms')
        min_size = request.GET.get('min_size')
        max_size = request.GET.get('max_size')
        has_photos = request.GET.get('has_photos')
        ordering = request.GET.get('ordering')
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius_km = request.GET.get('radius_km')

        queryset = Apartment.objects.filter(is_available=True)

        if location:
            queryset = queryset.filter(
                Q(city__icontains=location) |
                Q(country__icontains=location) |
                Q(address__icontains=location)
            )

        if lat and lng and radius_km:
            try:
                lat = float(lat)
                lng = float(lng)
                radius_km = float(radius_km)
                nearby_ids = [
                    apt.id for apt in queryset
                    if apt.latitude and apt.longitude and haversine_distance(lat, lng, apt.latitude, apt.longitude) <= radius_km
                ]
                queryset = queryset.filter(id__in=nearby_ids)
            except ValueError:
                pass

        if check_in and check_out:
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

                if check_in_date >= check_out_date:
                    return Response({'error': 'Check-out date must be after check-in date'}, status=status.HTTP_400_BAD_REQUEST)

                unavailable = Booking.objects.filter(
                    Q(start_date__lte=check_out_date) &
                    Q(end_date__gte=check_in_date) &
                    Q(status__in=['approved', 'pending'])
                ).values_list('apartment_id', flat=True)

                queryset = queryset.exclude(id__in=unavailable)

            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        elif check_in or check_out:
            return Response({'error': 'Both check_in and check_out must be provided together.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = queryset.filter(bedrooms__gte=(guests + 1) // 2)

        if bedrooms:
            try:
                queryset = queryset.filter(bedrooms__gte=int(bedrooms))
            except ValueError:
                pass
        if bathrooms:
            try:
                queryset = queryset.filter(bathrooms__gte=int(bathrooms))
            except ValueError:
                pass
        if min_size:
            try:
                queryset = queryset.filter(size_sqm__gte=int(min_size))
            except ValueError:
                pass
        if max_size:
            try:
                queryset = queryset.filter(size_sqm__lte=int(max_size))
            except ValueError:
                pass

        if min_price:
            try:
                queryset = queryset.filter(price_per_month__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                queryset = queryset.filter(price_per_month__lte=float(max_price))
            except ValueError:
                pass

        if property_type:
            queryset = queryset.filter(property_type__name__iexact=property_type)

        if amenities:
            for amenity in [a.strip() for a in amenities.split(',') if a.strip()]:
                queryset = queryset.filter(amenities__name__iexact=amenity)

        if has_photos and has_photos.lower() == 'true':
            queryset = queryset.filter(images__isnull=False).distinct()

        allowed_fields = ['price_per_month', '-price_per_month', 'size_sqm', '-size_sqm', 'created_at', '-created_at']
        if ordering in allowed_fields:
            queryset = queryset.order_by(ordering)

        queryset = queryset.distinct()
        serializer = ApartmentSearchSerializer(queryset, many=True)

        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })


class LocationAutocompleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) >= 2:
            locations = Apartment.objects.filter(
                Q(city__icontains=query) |
                Q(country__icontains=query)
            ).values('city', 'country').distinct()[:5]

            suggestions = [
                {
                    'city': loc['city'],
                    'country': loc['country'],
                    'display': f"{loc['city']}, {loc['country']}"
                }
                for loc in locations
            ]
            return Response({'suggestions': suggestions})
        return Response({'suggestions': []})

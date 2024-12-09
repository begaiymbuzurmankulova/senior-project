from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from .serializers import (
    UserSerializer, ApartmentSerializer, BookingSerializer,
    ReviewSerializer, AmenitySerializer
)
from apartments.models import Apartment, Amenity
from bookings.models import Booking
from reviews.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    serializer_class = ApartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'bedrooms', 'is_available']
    search_fields = ['title', 'description', 'address', 'city']
    ordering_fields = ['price_per_month', 'created_at', 'average_rating']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_images(self, request, pk=None):
        apartment = self.get_object()
        files = request.FILES.getlist('images')
        for file in files:
            apartment.images.create(image=file)
        return Response({'status': 'Images added'}, status=status.HTTP_201_CREATED)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'start_date']

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'landlord':
            return Booking.objects.filter(apartment__owner=user)
        return Booking.objects.filter(tenant=user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        booking = self.get_object()
        if request.user != booking.apartment.owner:
            return Response(
                {'error': 'Only the apartment owner can approve bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        booking.status = 'approved'
        booking.save()
        return Response({'status': 'Booking approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if request.user != booking.apartment.owner:
            return Response(
                {'error': 'Only the apartment owner can reject bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        booking.status = 'rejected'
        booking.save()
        return Response({'status': 'Booking rejected'})

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating']
    ordering_fields = ['created_at', 'rating']

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


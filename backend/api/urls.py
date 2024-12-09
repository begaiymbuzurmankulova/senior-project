from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ApartmentViewSet, BookingViewSet,
    ReviewViewSet, AmenityViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'apartments', ApartmentViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'amenities', AmenityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


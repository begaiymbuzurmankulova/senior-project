from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    UserViewSet, ApartmentViewSet, BookingViewSet,
    ReviewViewSet, AmenityViewSet
)
from apartments.views import (
    PropertySearchAPIView, LocationAutocompleteAPIView
)
from reviews.views import LandlordReviewViewSet

app_name = "api" 

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'apartments', ApartmentViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'amenities', AmenityViewSet)
router.register(r'landlord-reviews', LandlordReviewViewSet, basename='landlord-review')

urlpatterns = [
    path('', include(router.urls)),

    # JWT authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Search & autocomplete
    path('search/', PropertySearchAPIView.as_view(), name='apartment-search'),
    path('apartments/locations/', LocationAutocompleteAPIView.as_view(), name='location-autocomplete'),

]


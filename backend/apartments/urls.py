from django.urls import path
from . import views

app_name = 'apartments'

urlpatterns = [
    path('search/', views.PropertySearchAPIView.as_view(), name='api-search'),
    path('locations/autocomplete/', views.LocationAutocompleteAPIView.as_view(), name='api-location-autocomplete'),
    path('<int:pk>/', views.ApartmentDetailAPIView.as_view(), name='apartment-detail'),
]

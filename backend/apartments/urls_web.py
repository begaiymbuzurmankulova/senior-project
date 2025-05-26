from django.urls import path
from . import views

app_name = 'apartments'

urlpatterns = [
    path('search/', views.PropertySearchView.as_view(), name='search'),
    path('location-autocomplete/', views.location_autocomplete, name='location_autocomplete'),
]


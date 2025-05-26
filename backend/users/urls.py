from django.urls import path
from .views import RegisterView
from .views import VerifyEmailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
]

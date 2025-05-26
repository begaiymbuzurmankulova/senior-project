from django.urls import path
from .views import ChatGPTView

urlpatterns = [
    path('chatgpt/', ChatGPTView.as_view(), name='chatgpt'),
]

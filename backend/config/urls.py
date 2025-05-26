from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import HomeView
from users.views import RegisterView
from chatbot.views import ChatGPTView  # gpt
from django.contrib.auth import views as auth_views


schema_view = get_schema_view(
    openapi.Info(
        title="Your Project API",
        default_version='v1',
        description="API documentation for your platform",
        contact=openapi.Contact(email="you@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
)


urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api-auth/', include('rest_framework.urls')),  #  This adds login/logout UI
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),

    #Add namespace='api' here to allow reverse lookups like 'api:apartment-search'
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path('api/users/', include('users.urls')),
    path('api/auth/register/', RegisterView.as_view(), name='register'),


    path('favorites/', include('favorites.urls')),
    path('chatgpt/', ChatGPTView.as_view(), name='chatgpt'),
    path('api/', include('chatbot.urls')),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

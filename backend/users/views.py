from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import send_mail
from .utils import send_verification_email
from django.conf import settings
from django.urls import reverse
from django.core.signing import BadSignature, SignatureExpired
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner
from rest_framework.views import APIView

from .serializers import RegisterSerializer  # make sure this is the right import

User = get_user_model()
signer = TimestampSigner()



class RegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, JSONParser, FormParser]

    @swagger_auto_schema(
        operation_description="Register a new user and return JWT tokens.",
        request_body=RegisterSerializer,
        responses={201: 'Created', 400: 'Bad Request'},
        tags=["Auth"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_verified = False  # require verification
            user.save()

            send_verification_email(user, request)  # <--- send the email

            return Response({
                "detail": "Registration successful. Please verify your email."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            usigner.unsign(token, max_age=5184000) # 2 months
            user = User.objects.get(pk=user_id)
            user.is_verified = True
            user.save()
            return HttpResponse("Email verified successfully")
        except (BadSignature, SignatureExpired):
            return HttpResponse("Invalid or expired token", status=400)
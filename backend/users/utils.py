from django.core.signing import TimestampSigner
from django.urls import reverse


signer = TimestampSigner()

def generate_verification_token(user):
    return signer.sign(user.pk)

def send_verification_email(user, request):
    from .utils import generate_verification_token
    token = generate_verification_token(user)
    verification_url = request.build_absolute_uri(
        reverse("users:verify-email", args=[token])
    )
    send_mail(
        subject="Verify Your Email",
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=f"""
        <p>Hello {user.first_name},</p>
        <p>Thank you for registering. Please verify your email by clicking below:</p>
        <a href="{verification_url}">Verify My Email</a>
        <p>If you did not sign up, ignore this email.</p>
        """
    )


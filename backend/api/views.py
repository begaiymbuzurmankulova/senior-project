from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from django.utils import timezone
from bookings.models import BookingDocument




from bookings.models import Booking
from bookings.serializers import BookingSerializer, BookingDocumentUploadSerializer
from apartments.models import Apartment, Amenity
from apartments.serializers import ApartmentSerializer, AmenitySerializer
from users.serializers import UserSerializer
from reviews.models import Review, LandlordReview
from reviews.serializers import ReviewSerializer, LandlordReviewSerializer

# Get custom user model
User = get_user_model()

# Reusable Swagger response schemas
response_ok = openapi.Response(description="OK")
response_created = openapi.Response(description="Created")
response_bad = openapi.Response(description="Bad Request")
response_forbidden = openapi.Response(description="Forbidden")

upload_param = openapi.Parameter(
    'file', openapi.IN_FORM, description="Upload a document", type=openapi.TYPE_FILE
)


# --- ViewSets ---

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @swagger_auto_schema(tags=['Users'])
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.annotate(
        annotated_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    serializer_class = ApartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'bedrooms', 'is_available']
    search_fields = ['title', 'description', 'address', 'city']
    ordering_fields = ['price_per_month', 'created_at', 'annotated_rating', 'review_count']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(tags=['Apartments'])
    @action(detail=True, methods=['post'])
    def add_images(self, request, pk=None):
        apartment = self.get_object()
        files = request.FILES.getlist('images')
        for file in files:
            apartment.images.create(image=file)
        return Response({'status': 'Images added'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='availability')
    def check_availability(self, request, pk=None):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        start_date = date.fromisoformat(start_date_str) if start_date_str else date.today()
        end_date = date.fromisoformat(end_date_str) if end_date_str else start_date

        overlapping_bookings = Booking.objects.filter(
            apartment_id=pk,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status='approved'  # or whatever your active status is
        )

        available = not overlapping_bookings.exists()

        return Response({'available': available})


        # Gather all unavailable dates
        unavailable_dates = set()
        for booking in bookings:
            current = booking.check_in
            while current < booking.check_out:
                unavailable_dates.add(current.isoformat())
                current += timedelta(days=1)

        return Response({'unavailable_dates': sorted(unavailable_dates)}, status=status.HTTP_200_OK)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating']
    ordering_fields = ['created_at', 'rating']

    @swagger_auto_schema(tags=['Reviews'])
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class LandlordReviewViewSet(viewsets.ModelViewSet):
    queryset = LandlordReview.objects.all()
    serializer_class = LandlordReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=['Landlord Reviews'])
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



# --- Booking ViewSet ---

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'apartment', 'tenant']
    ordering_fields = ['start_date', 'created_at']

    def get_queryset(self):
        user = self.request.user
        outdated_bookings = Booking.objects.filter(
            status__in=['approved', 'pending'],
            end_date__lt=now().date()
        )
        outdated_bookings.update(status='completed')

        if user.user_type == 'landlord':
            return Booking.objects.filter(apartment__owner=user)
        return Booking.objects.filter(tenant=user)

    def perform_create(self, serializer):
        booking = serializer.save(tenant=self.request.user)
        send_mail(
            subject='Booking Confirmation',
            message=f"Thank you for your booking!\\n\\nApartment: {booking.apartment.title}\\nLocation: {booking.apartment.city}, {booking.apartment.country}\\nDates: {booking.start_date} to {booking.end_date}\\nTotal Price: {booking.total_price}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.tenant.email],
            fail_silently=True
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        booking = self.get_object()

        # Allow owner or admin
        if request.user != booking.apartment.owner and not request.user.is_staff:
            return Response({"error": "Only the apartment owner or admin can approve bookings"}, status=403)

        booking.status = 'approved'
        booking.approved_at = timezone.now()
        booking.save()

        return Response({"status": "Booking approved"})


    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()

        # Allow owner or admin
        if request.user != booking.apartment.owner and not request.user.is_staff:
            return Response({"error": "Only the apartment owner or admin can reject bookings"}, status=403)

        booking.status = 'rejected'
        booking.rejected_at = timezone.now()
        booking.save()

        return Response({"status": "Booking rejected"})


    @action(detail=True, methods=['post'], url_path='cancel')
    @swagger_auto_schema(responses={200: response_ok, 400: response_bad, 403: response_forbidden})
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if request.user != booking.tenant:
            return Response({'error': 'Only the tenant can cancel this booking.'}, status=status.HTTP_403_FORBIDDEN)
        if booking.status not in ['pending', 'approved']:
            return Response({'error': 'Only pending or approved bookings can be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = 'cancelled'
        booking.cancelled_at = now()
        booking.payment_status = 'refunded'
        booking.save()
        return Response({'status': 'Booking cancelled and marked for refund'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='request-refund')
    @swagger_auto_schema(responses={200: response_ok, 400: response_bad, 403: response_forbidden})
    def request_refund(self, request, pk=None):
        booking = self.get_object()
        if request.user != booking.tenant:
            return Response({'error': 'Only the tenant can request a refund.'}, status=status.HTTP_403_FORBIDDEN)
        if booking.refund_status != 'none':
            return Response({'error': 'Refund already requested or processed.'}, status=status.HTTP_400_BAD_REQUEST)
        booking.refund_status = 'requested'
        booking.refund_requested_at = now()
        booking.save()
        return Response({'status': 'Refund request submitted.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='process-refund')
    @swagger_auto_schema(responses={200: response_ok, 400: response_bad, 403: response_forbidden})
    def process_refund(self, request, pk=None):
        booking = self.get_object()
        if request.user != booking.apartment.owner:
            return Response({'error': 'Only the apartment owner can process the refund.'}, status=status.HTTP_403_FORBIDDEN)
        if booking.refund_status != 'requested':
            return Response({'error': 'Refund must be requested first.'}, status=status.HTTP_400_BAD_REQUEST)
        booking.refund_status = 'processed'
        booking.refund_processed_at = now()
        booking.payment_status = 'refunded'
        booking.save()
        return Response({'status': 'Refund processed successfully.'}, status=status.HTTP_200_OK)

    @action(
    detail=True,
    methods=['post'],
    url_path='upload-document',
    parser_classes=[MultiPartParser, FormParser],
    )
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'document_type',
                openapi.IN_FORM,
                description="Type of the document (e.g. ID, lease, etc.)",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'document',
                openapi.IN_FORM,
                description="Upload the document file (PDF, JPG, etc.)",
                type=openapi.TYPE_FILE,
                required=True
            )
        ]
    )
    def upload_document(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingDocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            BookingDocument.objects.create(
                booking=booking,
                document=serializer.validated_data['document'],
                document_type=serializer.validated_data['document_type']
            )
            return Response({'success': 'Document uploaded successfully'}, status=201)
        return Response(serializer.errors, status=400)
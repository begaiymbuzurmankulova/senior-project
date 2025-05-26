from django.db.models import Q
from datetime import datetime
from apartments.models import Apartment, ApartmentAvailability

def search_apartments(location=None, check_in=None, check_out=None, guests=None):
    apartments = Apartment.objects.filter(is_available=True)

    if location:
        apartments = apartments.filter(
            Q(city__icontains=location) | Q(address__icontains=location)
        )

    if guests:
        apartments = apartments.filter(max_guests__gte=guests)

    if check_in and check_out:
        # Parse dates
        try:
            check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            return Apartment.objects.none()

        # Only apartments with full availability in this range
        apartments = apartments.filter(
            availability_periods__start_date__lte=check_in,
            availability_periods__end_date__gte=check_out,
            availability_periods__is_available=True
        ).distinct()

    return apartments

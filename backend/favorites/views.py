from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Favorite
from .serializers import FavoriteSerializer
from apartments.models import Apartment

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        apartment_id = request.data.get('apartment_id')
        if not apartment_id:
            return Response({'error': 'apartment_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            apartment = Apartment.objects.get(id=apartment_id)
        except Apartment.DoesNotExist:
            return Response({'error': 'Apartment not found'}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=request.user, apartment=apartment)

        if not created:
            favorite.delete()
            return Response({'status': 'removed'})
        return Response({'status': 'added'})

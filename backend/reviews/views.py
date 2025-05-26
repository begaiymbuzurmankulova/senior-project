from django.shortcuts import render
from rest_framework import viewsets, permissions
from reviews.models import LandlordReview
from reviews.serializers import LandlordReviewSerializer

class LandlordReviewViewSet(viewsets.ModelViewSet):
    queryset = LandlordReview.objects.all()
    serializer_class = LandlordReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)




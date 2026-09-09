from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from .models import Store
from .serializers import StoreProfileSerializer, StoreSerializer


class StoreViewSet(viewsets.ModelViewSet):
    """Stores of the authenticated user only — tenancy enforced server-side."""

    serializer_class = StoreSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get", "put", "patch"], url_path="profile")
    def profile(self, request, pk=None):
        store = self.get_object()
        if request.method == "GET":
            return Response(StoreProfileSerializer(store.profile).data)
        serializer = StoreProfileSerializer(
            store.profile, data=request.data, partial=(request.method == "PATCH")
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

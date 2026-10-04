from django.db import transaction
from rest_framework import decorators, response, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Seller, Store, StoreItem
from .permissions import IsOwnerOrReadOnly
from .serializers import SellerSerializer, StoreItemSerializer, StoreSerializer

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class SellerViewSet(ModelViewSet):
    queryset = Seller.objects.select_related("user").all()
    serializer_class = SellerSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        if Seller.all_objects.filter(user=user).exists():
            raise PermissionDenied("You already have a seller profile.")
        serializer.save(user=user)
        if not user.is_seller:
            user.is_seller = True
            user.save(update_fields=["is_seller"])


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.select_related("owner", "owner__user").all()
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Writes only ever see the requesting seller's own stores.
        if self.request.method not in SAFE_METHODS:
            seller = getattr(self.request.user, "seller_profile", None)
            return qs.filter(owner=seller) if seller else qs.none()
        return qs

    def perform_create(self, serializer):
        seller = getattr(self.request.user, "seller_profile", None)
        if not seller:
            raise PermissionDenied("Create a seller profile first.")
        serializer.save(owner=seller)

    @decorators.action(detail=False, methods=["get"], url_path="mine", permission_classes=[IsAuthenticated])
    def mine(self, request):
        seller = getattr(request.user, "seller_profile", None)
        if not seller:
            return response.Response({"detail": "Not a seller."}, status=status.HTTP_403_FORBIDDEN)
        qs = self.get_queryset().filter(owner=seller)
        return response.Response(self.get_serializer(qs, many=True).data)


class StoreItemViewSet(ModelViewSet):
    # StoreItem has no ``product`` FK; selecting it made every list request fail with a 500.
    queryset = StoreItem.objects.select_related(
        "store", "store__owner", "store__owner__user", "variant", "variant__product"
    ).all()
    serializer_class = StoreItemSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method not in SAFE_METHODS:
            seller = getattr(self.request.user, "seller_profile", None)
            return qs.filter(store__owner=seller) if seller else qs.none()
        return qs

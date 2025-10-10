# marketplace/views.py (بروزرسانی)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Seller, Store, StoreItem
from .serializers import SellerSerializer, StoreSerializer, StoreItemSerializer
from .permissions import IsOwnerOrReadOnly

class SellerViewSet(ModelViewSet):
    queryset = Seller.objects.select_related("user").all()
    serializer_class = SellerSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        # هر کاربر فقط یک seller
        if hasattr(self.request.user, "seller_profile"):
            raise PermissionDenied("You already have a seller profile.")
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # خواندن برای همه آزاد است (فهرست عمومی)
        return super().get_queryset()


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.select_related("owner", "owner__user").all()
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        seller = getattr(self.request.user, "seller_profile", None)
        if not seller:
            raise PermissionDenied("Create a seller profile first.")
        serializer.save(owner=seller)

    def get_queryset(self):
        qs = super().get_queryset()
        # برای عملیات write، فقط فروشگاه‌های مالک را نشان بده
        if self.request.method not in ("GET", "HEAD", "OPTIONS") and self.request.user.is_authenticated:
            seller = getattr(self.request.user, "seller_profile", None)
            if seller:
                return qs.filter(owner=seller)
            return qs.none()
        return qs


class StoreItemViewSet(ModelViewSet):
    queryset = StoreItem.objects.select_related("store", "store__owner", "store__owner__user", "product", "variant", "variant__product").all()
    serializer_class = StoreItemSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        store = serializer.validated_data.get("store")
        seller = getattr(self.request.user, "seller_profile", None)
        if not seller or store.owner_id != seller.id:
            raise PermissionDenied("You can only add items to your own store.")
        serializer.save()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method not in ("GET", "HEAD", "OPTIONS") and self.request.user.is_authenticated:
            seller = getattr(self.request.user, "seller_profile", None)
            if seller:
                return qs.filter(store__owner=seller)
            return qs.none()
        return qs

from rest_framework import decorators, response, status
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

    # def perform_create(self, serializer):
    #     # هر کاربر فقط یک seller
    #     if hasattr(self.request.user, "seller_profile"):
    #         raise PermissionDenied("You already have a seller profile.")
    #     serializer.save(user=self.request.user)
    def perform_create(self, serializer):
        if hasattr(self.request.user, "seller_profile"):
            raise PermissionDenied("You already have a seller profile.")
        obj = serializer.save(user=self.request.user)
        # پرچم کاربر را هم‌زمان درست کنیم
        if not self.request.user.is_seller:
            self.request.user.is_seller = True
            self.request.user.save(update_fields=["is_seller"])
        return obj
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

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     # برای عملیات write، فقط فروشگاه‌های مالک را نشان بده
    #     if self.request.method not in ("GET", "HEAD", "OPTIONS") and self.request.user.is_authenticated:
    #         seller = getattr(self.request.user, "seller_profile", None)
    #         if seller:
    #             return qs.filter(owner=seller)
    #         return qs.none()
    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.path
        if p.startswith("/api/marketplace/..//stores"):
            if self.request.user.is_authenticated:
                seller = getattr(self.request.user, "seller_profile", None)
                return qs.filter(owner=seller) if seller else qs.none()
            return qs.none()
        if self.request.method not in ("GET", "HEAD", "OPTIONS") and self.request.user.is_authenticated:
            seller = getattr(self.request.user, "seller_profile", None)
            if seller:
                return qs.filter(owner=seller)
            return qs.none()
        return qs

    @decorators.action(detail=False, methods=["get"], url_path="mine")
    def mine(self, request):
        seller = getattr(request.user, "seller_profile", None)
        if not seller:
            return response.Response({"detail": "Not a seller."}, status=status.HTTP_403_FORBIDDEN)
        qs = self.get_queryset().filter(owner=seller)
        ser = self.get_serializer(qs, many=True)
        return response.Response(ser.data)

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

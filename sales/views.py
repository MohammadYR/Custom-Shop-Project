from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import Cart, CartItem, Order, OrderItem, create_order_from_cart
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer

class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related("items__store_item")

    def list(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="add-item")
    def add_item(self, request):
        """
        Add a store item to the user's cart.

        Accepts a request body with the following parameters:
        - store_item: The ID of the store item to add to the cart.
        - quantity: The quantity of the store item to add to the cart.

        Returns a response with the updated cart data.
        """
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data={**request.data, "cart": cart.id})
        serializer.is_valid(raise_exception=True)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            store_item=serializer.validated_data["store_item"],
            defaults={"quantity": serializer.validated_data["quantity"]},
        )
        if not created:
            item.quantity += serializer.validated_data["quantity"]
            item.save(update_fields=["quantity"])
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        """
        Checkout the user's cart and create an order.

        Returns a response with the created order data.

        Raises a 400_BAD_REQUEST error if the cart is empty or if the total price of the cart is zero.
        """
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            order = create_order_from_cart(cart)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related("store_item","cart")


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__store_item")

class OrderItemViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user).select_related("order","store_item")

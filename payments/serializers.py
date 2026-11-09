from rest_framework import serializers

from .models import Payment, Transaction


class StartPayResponseSerializer(serializers.Serializer):
    startpay_url = serializers.URLField()


class VerifyResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["success", "failed", "canceled"])
    ref_id = serializers.CharField(required=False, allow_blank=True)
    detail = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "ref_id", "status", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(source="order.status", read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "order_status",
            "amount",
            "provider",
            "authority",
            "status",
            "paid_at",
            "transactions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

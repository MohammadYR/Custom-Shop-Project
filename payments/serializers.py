from rest_framework import serializers


class StartPayResponseSerializer(serializers.Serializer):
    startpay_url = serializers.URLField()


class VerifyResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["success", "failed", "canceled"])
    ref_id = serializers.CharField(required=False, allow_blank=True)
    detail = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)

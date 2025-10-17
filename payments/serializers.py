from rest_framework import serializers


class StartPayParams(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)

class VerifyQueryParams(serializers.Serializer):
    Status = serializers.ChoiceField(choices=["OK", "NOK"])
    Authority = serializers.CharField(max_length=64)

class VerifySuccessResponse(serializers.Serializer):
    status = serializers.ChoiceField(choices=["success"])
    ref_id = serializers.CharField()

class EmptySerializer(serializers.Serializer):
    """Used for endpoints with no request body."""
    pass

class StartPayResponseSerializer(serializers.Serializer):
    startpay_url = serializers.URLField()

class VerifyResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["success", "failed","canceled"])
    ref_id = serializers.CharField(required=False, allow_blank=True)
    payload = serializers.JSONField(required=False)
    detail = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)
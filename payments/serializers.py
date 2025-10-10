from rest_framework import serializers

class StartPayParams(serializers.Serializer):

    order_id = serializers.IntegerField(min_value=1, required=True)

class VerifyQueryParams(serializers.Serializer):
    Status = serializers.ChoiceField(choices=["OK", "FAILED"], required=True)
    Authority = serializers.CharField(required=True, max_length=64)

class VerifySuccessResponse(serializers.Serializer):
    status = serializers.ChoiceField(choices=["success"])
    ref_id = serializers.CharField()

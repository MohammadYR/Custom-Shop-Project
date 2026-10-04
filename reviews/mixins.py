from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


class ReviewActionsMixin:
    """Adds ``{id}/review_create/`` (POST) and ``{id}/review_list/`` (GET) to a viewset.

    Subclasses set ``review_serializer_class`` and ``review_target_field``
    ("product" or "store").
    """

    review_serializer_class = None
    review_target_field = ""

    def _review_queryset(self, target):
        model = self.review_serializer_class.Meta.model
        return model.objects.filter(**{self.review_target_field: target}).select_related("user").order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="review_create", permission_classes=[IsAuthenticated])
    def review_create(self, request, pk=None):
        target = self.get_object()
        data = {key: value for key, value in request.data.items()}
        data[self.review_target_field] = str(target.pk)
        ser = self.review_serializer_class(data=data, context=self.get_serializer_context())
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="review_list", permission_classes=[AllowAny])
    def review_list(self, request, pk=None):
        reviews = self._review_queryset(self.get_object())
        page = self.paginate_queryset(reviews)
        ser = self.review_serializer_class(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(ser.data)


def review_schema(serializer_class):
    """extend_schema_view kwargs documenting the review actions for one viewset."""
    return {
        "review_create": extend_schema(
            summary="Create a review", request=serializer_class, responses={201: serializer_class}
        ),
        "review_list": extend_schema(summary="List reviews", responses={200: serializer_class(many=True)}),
    }

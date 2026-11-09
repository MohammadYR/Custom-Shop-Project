"""Regression tests for the reviews app."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from catalog.models import Category, Product
from reviews.models import ProductReview, StoreReview

pytestmark = pytest.mark.django_db


@pytest.fixture
def product():
    category = Category.objects.create(name="Review Cat")
    return Product.objects.create(category=category, title="Reviewed", price=10)


def test_clean_raises_validation_error_not_value_error(user, product):
    review = ProductReview(user=user, product=product, rating=9)
    with pytest.raises(ValidationError):
        review.full_clean()


def test_db_check_constraint_rejects_out_of_range_rating(user, product):
    with pytest.raises(IntegrityError), transaction.atomic():
        ProductReview.objects.create(user=user, product=product, rating=0)


def test_duplicate_review_returns_400_instead_of_500(auth_client, product):
    first = auth_client.post("/api/reviews/products/", {"product": str(product.id), "rating": 5}, format="json")
    assert first.status_code == 201
    dup = auth_client.post("/api/reviews/products/", {"product": str(product.id), "rating": 4}, format="json")
    assert dup.status_code == 400


def test_soft_deleted_review_does_not_block_a_new_one(user, product):
    old = ProductReview.objects.create(user=user, product=product, rating=2)
    old.delete()  # soft delete
    ProductReview.objects.create(user=user, product=product, rating=4)
    assert ProductReview.objects.filter(user=user, product=product).count() == 1


def test_review_target_cannot_be_moved(auth_client, user, product):
    other = Product.objects.create(category=product.category, title="Other", price=1)
    review = ProductReview.objects.create(user=user, product=product, rating=3)
    res = auth_client.patch(f"/api/reviews/products/{review.id}/", {"product": str(other.id)}, format="json")
    assert res.status_code == 400


def test_only_owner_can_edit_review(api_client, make_user, product):
    owner, intruder = make_user(), make_user()
    review = ProductReview.objects.create(user=owner, product=product, rating=3)
    api_client.force_authenticate(intruder)
    res = api_client.patch(f"/api/reviews/products/{review.id}/", {"rating": 1}, format="json")
    assert res.status_code == 403


def test_store_reviews_filter_by_user(api_client, make_user, make_store):
    store = make_store()
    u1, u2 = make_user(), make_user()
    StoreReview.objects.create(user=u1, store=store, rating=5)
    StoreReview.objects.create(user=u2, store=store, rating=4)
    res = api_client.get(f"/api/reviews/stores/?user={u1.id}")
    assert res.status_code == 200
    assert res.json()["count"] == 1

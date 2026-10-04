"""Spec paths: /api/categories/, /api/admin/categories/, /api/products/, /api/stores/, review_create."""
import pytest

from catalog.models import Category, Product
from reviews.models import ProductReview, StoreReview

pytestmark = pytest.mark.django_db


def test_public_categories_are_read_only(api_client, auth_client):
    Category.objects.create(name="Books")
    res = api_client.get("/api/categories/")
    assert res.status_code == 200 and res.data["count"] == 1
    assert auth_client.post("/api/categories/", {"name": "X"}, format="json").status_code == 405


def test_admin_categories_crud(staff_client, auth_client):
    assert auth_client.get("/api/admin/categories/").status_code == 403
    res = staff_client.post("/api/admin/categories/", {"name": "Toys"}, format="json")
    assert res.status_code == 201
    cid = res.data["id"]
    assert staff_client.patch(f"/api/admin/categories/{cid}/", {"name": "Games"}, format="json").status_code == 200
    assert staff_client.delete(f"/api/admin/categories/{cid}/").status_code == 204
    assert not Category.objects.filter(pk=cid).exists()


def test_products_public_list_hides_inactive(api_client, make_store_item):
    item = make_store_item()
    Product.objects.create(category=item.variant.product.category, title="Hidden", price=1, is_active=False)
    res = api_client.get("/api/products/")
    assert [p["title"] for p in res.data["results"]] == [item.variant.product.title]
    assert api_client.get(f"/api/products/{item.variant.product_id}/").status_code == 200


def test_product_review_create_and_list(api_client, auth_client, user, make_store_item):
    product = make_store_item().variant.product
    url = f"/api/products/{product.id}/review_create/"
    assert api_client.post(url, {"rating": 5}, format="json").status_code == 401
    res = auth_client.post(url, {"rating": 5, "comment": "Great"}, format="json")
    assert res.status_code == 201
    assert ProductReview.objects.get(product=product).user == user
    assert auth_client.post(url, {"rating": 4}, format="json").status_code == 400  # one review per user
    assert auth_client.post(url, {"rating": 9}, format="json").status_code == 400
    listing = api_client.get(f"/api/products/{product.id}/review_list/")
    assert listing.status_code == 200 and listing.data["count"] == 1


def test_store_review_create_and_store_items(api_client, auth_client, make_store, make_store_item):
    store = make_store()
    make_store_item(store=store)
    res = auth_client.post(f"/api/stores/{store.id}/review_create/", {"rating": 3}, format="json")
    assert res.status_code == 201
    assert StoreReview.objects.filter(store=store).count() == 1
    assert api_client.get("/api/stores/").data["count"] == 1
    items = api_client.get(f"/api/stores/{store.id}/items/")
    assert items.status_code == 200 and items.data["count"] == 1


def test_inactive_store_hidden(api_client, make_store):
    make_store(is_active=False)
    assert api_client.get("/api/stores/").data["count"] == 0

"""Product listing: search, filters, ordering, stock / best price, images."""
import io
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from catalog.models import Category, Product, ProductImage, ProductVariant
from marketplace.models import StoreItem
from reviews.models import ProductReview

pytestmark = pytest.mark.django_db
URL = "/api/catalog/products/"


@pytest.fixture
def catalog(make_store):
    phones = Category.objects.create(name="Phones")
    books = Category.objects.create(name="Books")
    p1 = Product.objects.create(category=phones, title="Galaxy Phone", description="android", price=Decimal("500"))
    p2 = Product.objects.create(category=phones, title="iPhone", description="ios", price=Decimal("900"))
    p3 = Product.objects.create(category=books, title="Django Book", description="python web", price=Decimal("30"))
    s1, s2 = make_store(), make_store()
    for product, store, price, stock, sku in [
        (p1, s1, "480", 3, "A"), (p1, s2, "470", 2, "B"), (p2, s1, "880", 0, "C"),
    ]:
        variant, _ = ProductVariant.objects.get_or_create(product=product, name="Default")
        StoreItem.objects.create(store=store, variant=variant, sku=sku, price=Decimal(price), stock=stock)
    return {"phones": phones, "books": books, "p1": p1, "p2": p2, "p3": p3, "s1": s1, "s2": s2}


def _titles(res):
    assert res.status_code == 200, res.content
    return [p["title"] for p in res.json()["results"]]


def test_search(api_client, catalog):
    assert _titles(api_client.get(URL, {"search": "python"})) == ["Django Book"]
    assert set(_titles(api_client.get(URL, {"search": "phone"}))) == {"Galaxy Phone", "iPhone"}


def test_filter_by_category_and_price(api_client, catalog):
    res = api_client.get(URL, {"category": str(catalog["phones"].id), "max_price": "600"})
    assert _titles(res) == ["Galaxy Phone"]
    assert _titles(api_client.get(URL, {"category_slug": "books"})) == ["Django Book"]


def test_filter_in_stock_and_store(api_client, catalog):
    assert _titles(api_client.get(URL, {"in_stock": "true"})) == ["Galaxy Phone"]
    assert _titles(api_client.get(URL, {"store": str(catalog["s1"].id)})) == ["Galaxy Phone", "iPhone"]


def test_ordering(api_client, catalog):
    assert _titles(api_client.get(URL, {"ordering": "-price"})) == ["iPhone", "Galaxy Phone", "Django Book"]


def test_stock_best_price_and_rating(api_client, catalog, user):
    ProductReview.objects.create(user=user, product=catalog["p1"], rating=4)
    data = {p["title"]: p for p in api_client.get(URL).json()["results"]}
    assert data["Galaxy Phone"]["stock"] == 5
    assert Decimal(data["Galaxy Phone"]["best_price"]) == Decimal("470")
    assert Decimal(data["Galaxy Phone"]["rating"]) == Decimal("4")
    assert data["Galaxy Phone"]["reviews_count"] == 1
    assert data["iPhone"]["stock"] == 0
    assert data["iPhone"]["best_price"] is None  # nobody has it in stock
    assert data["Django Book"]["name"] == "Django Book"


def test_pagination(api_client, catalog):
    res = api_client.get(URL, {"page_size": 2})
    body = res.json()
    assert body["count"] == 3
    assert len(body["results"]) == 2
    assert body["next"]


def _png():
    buf = io.BytesIO()
    Image.new("RGB", (2, 2), "red").save(buf, format="PNG")
    return SimpleUploadedFile("p.png", buf.getvalue(), content_type="image/png")


def test_staff_can_upload_multiple_images(staff_client, api_client, catalog, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    for order in (1, 0):
        res = staff_client.post(
            "/api/catalog/product-images/",
            {"product": str(catalog["p3"].id), "image": _png(), "sort_order": order},
            format="multipart",
        )
        assert res.status_code == 201, res.content
    assert ProductImage.objects.filter(product=catalog["p3"]).count() == 2
    detail = api_client.get(f"{URL}{catalog['p3'].id}/").json()
    assert [img["sort_order"] for img in detail["images"]] == [0, 1]


def test_regular_user_cannot_upload_images(auth_client, catalog):
    res = auth_client.post("/api/catalog/product-images/", {"product": str(catalog["p3"].id)}, format="multipart")
    assert res.status_code == 403

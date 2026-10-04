import pytest

from catalog.models import Category, Product

pytestmark = pytest.mark.django_db


def test_category_crud(staff_client, api_client):
    # create (staff only)
    resp = staff_client.post("/api/catalog/categories/", {"name": "Phones"}, format="json")
    assert resp.status_code == 201
    cid = resp.data["id"]
    # list (public)
    resp = api_client.get("/api/catalog/categories/")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    # retrieve (public)
    resp = api_client.get(f"/api/catalog/categories/{cid}/")
    assert resp.status_code == 200


def test_product_crud(staff_client, api_client):
    cat = Category.objects.create(name="Laptops")
    payload = {"category": str(cat.id), "title": "ThinkPad X1", "price": "1999.99"}
    resp = staff_client.post("/api/catalog/products/", payload, format="json")
    assert resp.status_code == 201
    pid = resp.data["id"]
    resp = api_client.get("/api/catalog/products/")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    resp = api_client.get(f"/api/catalog/products/{pid}/")
    assert resp.status_code == 200


# --- regression: catalog was writable by anonymous users (AllowAny) ---------

@pytest.mark.parametrize(
    "url,payload",
    [
        ("/api/catalog/categories/", {"name": "Hacked"}),
        ("/api/catalog/products/", {"title": "Hacked", "price": "1"}),
        ("/api/catalog/product-variants/", {"name": "Hacked"}),
    ],
)
def test_anonymous_cannot_write_catalog(api_client, url, payload):
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 401


def test_regular_user_cannot_write_catalog(auth_client):
    cat = Category.objects.create(name="Books")
    resp = auth_client.post("/api/catalog/categories/", {"name": "Hacked"}, format="json")
    assert resp.status_code == 403
    resp = auth_client.patch(f"/api/catalog/categories/{cat.id}/", {"name": "Renamed"}, format="json")
    assert resp.status_code == 403
    resp = auth_client.delete(f"/api/catalog/categories/{cat.id}/")
    assert resp.status_code == 403


# --- regression: Persian names produced empty / duplicate slugs -------------

def test_persian_names_get_unique_unicode_slugs():
    first = Category.objects.create(name="موبایل")
    second = Category.objects.create(name="موبایل!")  # slugifies to the same value
    assert first.slug == "موبایل"
    assert second.slug == "موبایل-2"

    p1 = Product.objects.create(category=first, title="گوشی", price=1)
    p2 = Product.objects.create(category=first, title="گوشی", price=2)
    assert p1.slug and p2.slug and p1.slug != p2.slug


def test_symbol_only_name_falls_back_to_a_non_empty_slug():
    a = Category.objects.create(name="!!!")
    b = Category.objects.create(name="???")
    assert a.slug == "category"
    assert b.slug == "category-2"


# --- regression: soft-deleted category blocked re-creating the same name ----

def test_category_name_reusable_after_soft_delete(staff_client):
    old = Category.objects.create(name="Phones")
    old.delete()
    resp = staff_client.post("/api/catalog/categories/", {"name": "Phones"}, format="json")
    assert resp.status_code == 201
    assert resp.data["slug"] == "phones-2"


def test_duplicate_category_name_is_400(staff_client):
    Category.objects.create(name="Phones")
    resp = staff_client.post("/api/catalog/categories/", {"name": "phones"}, format="json")
    assert resp.status_code == 400

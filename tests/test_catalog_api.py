import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from catalog.models import Category, Product

pytestmark = pytest.mark.django_db

def test_category_crud():
    client = APIClient()
    # create
    resp = client.post("/api/catalog/categories/", {"name": "Phones"}, format="json")
    assert resp.status_code == 201
    cid = resp.data["id"]
    # list
    resp = client.get("/api/catalog/categories/")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    # retrieve
    resp = client.get(f"/api/catalog/categories/{cid}/")
    assert resp.status_code == 200

def test_product_crud():
    client = APIClient()
    cat = Category.objects.create(name="Laptops")
    # create
    payload = {"category": str(cat.id), "title": "ThinkPad X1", "price": "1999.99"}
    resp = client.post("/api/catalog/products/", payload, format="json")
    assert resp.status_code == 201
    pid = resp.data["id"]
    # list
    resp = client.get("/api/catalog/products/")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    # retrieve
    resp = client.get(f"/api/catalog/products/{pid}/")
    assert resp.status_code == 200

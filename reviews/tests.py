import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from catalog.models import Product, Category
from marketplace.models import Store, Seller

@pytest.mark.django_db
def test_product_review_crud_and_uniqueness():
    User = get_user_model()
    u = User.objects.create_user(username="u", email="u@ex.com", password="p")
    cat = Category.objects.create(name="Cat")
    p = Product.objects.create(title="Phone", category=cat)

    c = APIClient(); c.force_authenticate(user=u)

    # create
    res = c.post("/api/reviews/products/", {"product": p.id, "rating": 5, "comment": "great"}, format="json")
    assert res.status_code == 201
    rid = res.json()["id"]

    # duplicate review should fail by unique_together
    res_dup = c.post("/api/reviews/products/", {"product": p.id, "rating": 4}, format="json")
    assert res_dup.status_code in (400, 500)

    # patch by owner
    res_up = c.patch(f"/api/reviews/products/{rid}/", {"rating": 4}, format="json")
    assert res_up.status_code == 200
    assert res_up.json()["rating"] == 4

    # list (public)
    c2 = APIClient()
    res_list = c2.get(f"/api/reviews/products/?product={p.id}")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

@pytest.mark.django_db
def test_store_review_and_filtering():
    User = get_user_model()
    u = User.objects.create_user(username="u1", email="u1@ex.com", password="p")
    seller = Seller.objects.create(user=u, display_name="S1")
    store = Store.objects.create(owner=seller, name="S1-Shop")

    c = APIClient(); c.force_authenticate(user=u)

    res = c.post("/api/reviews/stores/", {"store": store.id, "rating": 3, "comment": "ok"}, format="json")
    assert res.status_code == 201

    # filter by store
    res_list = c.get(f"/api/reviews/stores/?store={store.id}")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # filter by user
    res_list = c.get(f"/api/reviews/stores/?user={u.id}")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from marketplace.models import Seller, Store

@pytest.mark.django_db
def test_mystore_lists_only_my_stores():
    User = get_user_model()
    u1 = User.objects.create_user(username="a", email="a@ex.com", password="p")
    u2 = User.objects.create_user(username="b", email="b@ex.com", password="p")
    s1 = Seller.objects.create(user=u1, display_name="S1")
    s2 = Seller.objects.create(user=u2, display_name="S2")
    Store.objects.create(owner=s1, name="A-Shop")
    Store.objects.create(owner=s2, name="B-Shop")

    client = APIClient(); client.force_authenticate(user=u1)
    res = client.get("/api/marketplace/..//stores/")   # alias mystore
    assert res.status_code == 200
    names = [st["name"] for st in res.json()]
    assert names == ["A-Shop"]

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from faker import Faker
from .models import Tender, Tag, Bid
from users.models import User

fake = Faker()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def client_user():
    return User.objects.create_user(
        username=fake.user_name(),
        password=fake.password(),
        is_client=True
    )

@pytest.fixture
def vendor_user():
    return User.objects.create_user(
        username=fake.user_name(),
        password=fake.password(),
        is_vendor=True
    )

@pytest.fixture
def tender(client_user):
    return Tender.objects.create(
        client=client_user,
        title=fake.sentence(),
        description=fake.text(),
        max_duration=30,
        min_budget=1000,
        max_budget=5000,
        deadline=fake.future_date()
    )

@pytest.mark.django_db
class TestTenderEndpoints:
    def test_list_tenders(self, api_client, client_user):
        api_client.force_authenticate(user=client_user)
        response = api_client.get(reverse('tender-list'))
        assert response.status_code == status.HTTP_200_OK

    def test_create_tender(self, api_client, client_user):
        api_client.force_authenticate(user=client_user)
        data = {
            'title': fake.sentence(),
            'description': fake.text(),
            'max_duration': 30,
            'min_budget': 1000,
            'max_budget': 5000,
            'deadline': fake.future_date().isoformat()
        }
        response = api_client.post(reverse('tender-list'), data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_place_bid(self, api_client, vendor_user, tender):
        api_client.force_authenticate(user=vendor_user)
        data = {
            'amount': 2000,
            'proposal': fake.text(),
            'delivery_time': 20
        }
        response = api_client.post(
            reverse('tender-place-bid', kwargs={'pk': tender.tender_id}),
            data
        )
        assert response.status_code == status.HTTP_201_CREATED

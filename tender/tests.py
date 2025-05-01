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
    user = User.objects.create_user(
        username=fake.user_name(),
        password=fake.password()
    )
    user.is_vendor = True
    user.save()
    return user

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

@pytest.fixture
def tender_with_bid(tender, vendor_user):
    bid = Bid.objects.create(
        tender=tender,
        vendor=vendor_user,
        amount=2000,
        proposal=fake.text(),
        delivery_time=20
    )
    return tender, bid

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
        
        bid = Bid.objects.filter(tender=tender, vendor=vendor_user).first()
        assert bid is not None
        assert bid.amount == 2000
        assert bid.status == 'pending'

    def test_vendor_cannot_create_tender(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        data = {
            'title': fake.sentence(),
            'description': fake.text(),
            'max_duration': 30,
            'min_budget': 1000,
            'max_budget': 5000,
            'deadline': fake.future_date().isoformat()
        }
        response = api_client.post(reverse('tender-list'), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_client_cannot_place_bid(self, api_client, client_user, tender):
        api_client.force_authenticate(user=client_user)
        data = {
            'amount': 2000,
            'proposal': fake.text(),
            'delivery_time': 20
        }
        response = api_client.post(
            reverse('tender-place-bid', kwargs={'pk': tender.tender_id}),
            data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_vendor_cannot_bid_twice(self, api_client, tender_with_bid):
        tender, existing_bid = tender_with_bid
        api_client.force_authenticate(user=existing_bid.vendor)
        data = {
            'amount': 1800,  # Lower amount
            'proposal': fake.text(),
            'delivery_time': 15
        }
        response = api_client.post(
            reverse('tender-place-bid', kwargs={'pk': tender.tender_id}),
            data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_place_bid_on_closed_tender(self, api_client, vendor_user, tender):
        tender.status = 'completed'
        tender.save()
        
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
        assert response.status_code == status.HTTP_400_BAD_REQUEST

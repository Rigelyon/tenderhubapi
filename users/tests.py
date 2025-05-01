import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from faker import Faker
from .models import User, VendorProfile, ClientProfile

fake = Faker()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestUserEndpoints:
    def test_user_registration_client(self, api_client):
        data = {
            'username': fake.user_name(),
            'password': 'testpass123',
            'password2': 'testpass123',
            'email': fake.email(),
            'user_type': 'client'
        }
        response = api_client.post(reverse('register'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=data['username']).exists()

    def test_user_registration_vendor(self, api_client):
        data = {
            'username': fake.user_name(),
            'password': 'testpass123',
            'password2': 'testpass123',
            'email': fake.email(),
            'user_type': 'vendor'
        }
        response = api_client.post(reverse('register'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=data['username']).exists()

    def test_user_profile(self, api_client):
        user = User.objects.create_user(
            username=fake.user_name(),
            password=fake.password()
        )
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse('user-profile'))
        assert response.status_code == status.HTTP_200_OK

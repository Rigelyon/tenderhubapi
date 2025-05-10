import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from faker import Faker
from .models import User, VendorProfile, ClientProfile, Portfolio
from datetime import date

fake = Faker()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def vendor_user():
    user = User.objects.create_user(
        username=fake.user_name(),
        password='testpass123',
        is_vendor=True
    )
    vendor_profile = VendorProfile.objects.create(user=user)
    return user

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

@pytest.mark.django_db
class TestPortfolioEndpoints:
    def test_add_portfolio(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        data = {
            'title': fake.sentence(),
            'description': fake.paragraph(),
            'date_created': date.today().isoformat()
        }
        url = reverse('vendor-add-portfolio', kwargs={'pk': 'me'})
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Portfolio.objects.filter(title=data['title']).exists()
    
    def test_delete_portfolio(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        vendor_profile = vendor_user.vendor_profile
        
        # Buat portofolio terlebih dahulu
        portfolio = Portfolio.objects.create(
            vendor=vendor_profile,
            title=fake.sentence(),
            description=fake.paragraph(),
            date_created=date.today()
        )
        
        # Coba hapus portofolio
        url = reverse('vendor-delete-portfolio', kwargs={'pk': 'me'})
        response = api_client.delete(f"{url}?portfolio_id={portfolio.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Portfolio.objects.filter(id=portfolio.id).exists()
    
    def test_delete_portfolio_not_found(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        
        # Coba hapus portofolio yang tidak ada
        url = reverse('vendor-delete-portfolio', kwargs={'pk': 'me'})
        response = api_client.delete(f"{url}?portfolio_id=9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_portfolio_missing_id(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        
        # Coba hapus tanpa menyediakan portfolio_id
        url = reverse('vendor-delete-portfolio', kwargs={'pk': 'me'})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

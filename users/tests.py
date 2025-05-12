import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from faker import Faker
from .models import User, VendorProfile, ClientProfile, Portfolio, Skill, Education
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

@pytest.mark.django_db
class TestSkillEndpoints:
    def test_list_skills(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        url = reverse('vendor-skills', kwargs={'pk': 'me'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    def test_add_skill_by_name(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        data = {
            'name': fake.word() + ' Programming'
        }
        url = reverse('vendor-add-skill', kwargs={'pk': 'me'})
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'created' in response.data
        assert response.data['message'].startswith(f"Skill '{data['name']}'")
        
        # Verify skill was added to vendor profile
        vendor_profile = VendorProfile.objects.get(user=vendor_user)
        assert vendor_profile.skills.filter(name=data['name']).exists()
    
    def test_add_existing_skill_by_id(self, api_client, vendor_user):
        # Create a skill first
        skill = Skill.objects.create(name=fake.word() + ' Development')
        
        api_client.force_authenticate(user=vendor_user)
        data = {
            'id': skill.id
        }
        url = reverse('vendor-add-skill', kwargs={'pk': 'me'})
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'].startswith(f"Skill '{skill.name}'")
        
        # Verify skill was added to vendor profile
        vendor_profile = VendorProfile.objects.get(user=vendor_user)
        assert vendor_profile.skills.filter(id=skill.id).exists()
    
    def test_add_skill_missing_params(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        data = {}  # Empty data
        url = reverse('vendor-add-skill', kwargs={'pk': 'me'})
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_delete_skill(self, api_client, vendor_user):
        # Create a skill and add it to vendor profile
        skill = Skill.objects.create(name=fake.word() + ' Programming')
        vendor_profile = VendorProfile.objects.get(user=vendor_user)
        vendor_profile.skills.add(skill)
        
        api_client.force_authenticate(user=vendor_user)
        url = reverse('vendor-delete-skill', kwargs={'pk': 'me'})
        response = api_client.delete(f"{url}?skill_id={skill.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'].startswith(f"Skill '{skill.name}'")
        
        # Verify skill was removed from vendor profile
        vendor_profile = VendorProfile.objects.get(user=vendor_user)
        assert not vendor_profile.skills.filter(id=skill.id).exists()
    
    def test_delete_skill_not_in_profile(self, api_client, vendor_user):
        # Create a skill but don't add it to vendor profile
        skill = Skill.objects.create(name=fake.word() + ' Expertise')
        
        api_client.force_authenticate(user=vendor_user)
        url = reverse('vendor-delete-skill', kwargs={'pk': 'me'})
        response = api_client.delete(f"{url}?skill_id={skill.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_delete_skill_missing_id(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        url = reverse('vendor-delete-skill', kwargs={'pk': 'me'})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

@pytest.mark.django_db
class TestCertificationEndpoints:
    def test_delete_certification(self, api_client, vendor_user):
        # Adding complete test for certification deletion functionality
        from .models import Certification
        vendor_profile = VendorProfile.objects.get(user=vendor_user)
        
        # Create a certification
        certification = Certification.objects.create(
            vendor=vendor_profile,
            title=fake.word() + " Certification",
            issuing_organization=fake.company(),
            issue_date=date.today()
        )
        
        api_client.force_authenticate(user=vendor_user)
        url = reverse('vendor-delete-certification', kwargs={'pk': 'me'})
        response = api_client.delete(f"{url}?certification_id={certification.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Certification.objects.filter(id=certification.id).exists()
        
    def test_delete_certification_not_found(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        
        # Try to delete a non-existent certification
        url = reverse('vendor-delete-certification', kwargs={'pk': 'me'})
        response = api_client.delete(f"{url}?certification_id=9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_delete_certification_missing_id(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        
        # Try to delete without providing certification_id
        url = reverse('vendor-delete-certification', kwargs={'pk': 'me'})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestEducationEndpoints:
    def test_add_education(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        data = {
            'institution': fake.company() + " University",
            'degree': fake.word() + " Degree",
            'field_of_study': fake.word() + " Studies",
            'start_date': date.today().isoformat()
        }
        url = reverse('vendor-add-education', kwargs={'pk': 'me'})
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Education.objects.filter(institution=data['institution']).exists()
    
    def test_list_education(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        vendor_profile = VendorProfile.objects.get(user=vendor_user)
        
        # Create two education records
        Education.objects.create(
            vendor=vendor_profile,
            institution=fake.company() + " University",
            degree=fake.word() + " Degree",
            field_of_study=fake.word() + " Studies",
            start_date=date.today()
        )
        
        Education.objects.create(
            vendor=vendor_profile,
            institution=fake.company() + " College",
            degree=fake.word() + " Certificate",
            field_of_study=fake.word() + " Major",
            start_date=date.today()
        )
        
        url = reverse('vendor-education', kwargs={'pk': 'me'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_delete_education(self, api_client, vendor_user):
        # Adding complete test for education deletion functionality
        from .models import Education
        vendor_profile = VendorProfile.objects.get(user=vendor_user)
        
        # Create an education record using available Faker methods
        education = Education.objects.create(
            vendor=vendor_profile,
            institution=fake.company() + " University",  # Using company() instead of university()
            degree=fake.word() + " Degree",
            field_of_study=fake.word() + " Studies",
            start_date=date.today()
        )
        
        api_client.force_authenticate(user=vendor_user)
        url = reverse('vendor-delete-education', kwargs={'pk': 'me'})
        response = api_client.delete(f"{url}?education_id={education.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Education.objects.filter(id=education.id).exists()
        
    def test_delete_education_not_found(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        
        # Try to delete a non-existent education record
        url = reverse('vendor-delete-education', kwargs={'pk': 'me'})
        response = api_client.delete(f"{url}?education_id=9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_delete_education_missing_id(self, api_client, vendor_user):
        api_client.force_authenticate(user=vendor_user)
        
        # Try to delete without providing education_id
        url = reverse('vendor-delete-education', kwargs={'pk': 'me'})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from faker import Faker
from tender.models import Project, Tender
from .models import ProjectActivity
from users.models import User

fake = Faker()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def client_user():
    return User.objects.create_user(
        username=fake.user_name(),
        is_client=True,
        password=fake.password()
    )

@pytest.fixture
def vendor_user():
    return User.objects.create_user(
        username=fake.user_name(),
        is_vendor=True,
        password=fake.password()
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

@pytest.fixture
def project(tender, client_user, vendor_user):
    return Project.objects.create(
        tender=tender,
        client=client_user,
        vendor=vendor_user,
        agreed_amount=1000,
        deadline=tender.deadline
    )

@pytest.mark.django_db
class TestProjectActivityEndpoints:
    def test_list_activities(self, api_client, project):
        api_client.force_authenticate(user=project.client)
        response = api_client.get(
            reverse('project-activities-list', kwargs={'project_pk': project.project_id})
        )
        assert response.status_code == status.HTTP_200_OK

    def test_create_activity(self, api_client, project):
        api_client.force_authenticate(user=project.client)
        data = {
            'activity_type': 'comment',
            'description': fake.text()
        }
        response = api_client.post(
            reverse('project-activities-list', kwargs={'project_pk': project.project_id}),
            data
        )
        assert response.status_code == status.HTTP_201_CREATED

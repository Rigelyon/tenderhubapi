import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from faker import Faker
from tender.models import Project
from .models import ProjectActivity
from users.models import User

fake = Faker()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def project(db):
    client = User.objects.create_user(username=fake.user_name(), is_client=True)
    vendor = User.objects.create_user(username=fake.user_name(), is_vendor=True)
    return Project.objects.create(
        tender=None,  # You'll need to create a tender first
        client=client,
        vendor=vendor,
        agreed_amount=1000,
        deadline=fake.future_date()
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

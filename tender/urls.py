from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    TenderViewSet, BidViewSet, ProjectViewSet, 
    ProjectActivityViewSet, TagViewSet
)

router = DefaultRouter()
router.register(r'tenders', TenderViewSet, basename='tender')
router.register(r'bids', BidViewSet, basename='bid')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tags', TagViewSet)

# Nested routers for project activities
projects_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
projects_router.register(r'activities', ProjectActivityViewSet, basename='project-activities')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
]
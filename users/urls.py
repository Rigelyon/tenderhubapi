from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, UserProfileView, ClientProfileView, 
    VendorProfileViewSet, SkillViewSet, ReviewViewSet
)

router = DefaultRouter()
router.register(r'vendors', VendorProfileViewSet, basename='vendor')
router.register(r'skills', SkillViewSet)
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('client-profile/', ClientProfileView.as_view(), name='client-profile'),
    path('', include(router.urls)),
]
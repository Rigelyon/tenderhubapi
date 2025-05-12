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

# Adding specific names for vendor actions to simplify testing
vendor_detail = VendorProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

vendor_skills = VendorProfileViewSet.as_view({
    'get': 'skills',
})

vendor_add_skill = VendorProfileViewSet.as_view({
    'post': 'add_skill',
})

vendor_delete_skill = VendorProfileViewSet.as_view({
    'delete': 'delete_skill',
})

vendor_portfolios = VendorProfileViewSet.as_view({
    'get': 'portfolios',
})

vendor_add_portfolio = VendorProfileViewSet.as_view({
    'post': 'add_portfolio',
})

vendor_delete_portfolio = VendorProfileViewSet.as_view({
    'delete': 'delete_portfolio',
})

vendor_certifications = VendorProfileViewSet.as_view({
    'get': 'certifications',
})

vendor_add_certification = VendorProfileViewSet.as_view({
    'post': 'add_certification',
})

vendor_delete_certification = VendorProfileViewSet.as_view({
    'delete': 'delete_certification',
})

vendor_education = VendorProfileViewSet.as_view({
    'get': 'education',
})

vendor_add_education = VendorProfileViewSet.as_view({
    'post': 'add_education',
})

vendor_delete_education = VendorProfileViewSet.as_view({
    'delete': 'delete_education',
})

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('client-profile/', ClientProfileView.as_view(), name='client-profile'),
    
    # Named URL patterns for vendor actions
    path('vendors/<pk>/', vendor_detail, name='vendor-detail'),
    path('vendors/<pk>/skills/', vendor_skills, name='vendor-skills'),
    path('vendors/<pk>/add_skill/', vendor_add_skill, name='vendor-add-skill'),
    path('vendors/<pk>/delete_skill/', vendor_delete_skill, name='vendor-delete-skill'),
    path('vendors/<pk>/portfolios/', vendor_portfolios, name='vendor-portfolios'),
    path('vendors/<pk>/add_portfolio/', vendor_add_portfolio, name='vendor-add-portfolio'),
    path('vendors/<pk>/delete_portfolio/', vendor_delete_portfolio, name='vendor-delete-portfolio'),
    path('vendors/<pk>/certifications/', vendor_certifications, name='vendor-certifications'),
    path('vendors/<pk>/add_certification/', vendor_add_certification, name='vendor-add-certification'),
    path('vendors/<pk>/delete_certification/', vendor_delete_certification, name='vendor-delete-certification'),
    path('vendors/<pk>/education/', vendor_education, name='vendor-education'),
    path('vendors/<pk>/add_education/', vendor_add_education, name='vendor-add-education'),
    path('vendors/<pk>/delete_education/', vendor_delete_education, name='vendor-delete-education'),
    
    path('', include(router.urls)),
]
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import (
    User, ClientProfile, VendorProfile, Portfolio, 
    Certification, Education, Review, Skill
)
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, ClientProfileSerializer,
    VendorProfileSerializer, PortfolioSerializer, CertificationSerializer,
    EducationSerializer, ReviewSerializer, SkillSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ClientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(ClientProfile, user=self.request.user)

class VendorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.action == 'list':
            return VendorProfile.objects.all()
        return VendorProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return get_object_or_404(VendorProfile, user=self.request.user)
        return super().get_object()
    
    @action(detail=True, methods=['get'])
    def portfolios(self, request, pk=None):
        vendor = self.get_object()
        portfolios = Portfolio.objects.filter(vendor=vendor)
        serializer = PortfolioSerializer(portfolios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_portfolio(self, request, pk=None):
        vendor = self.get_object()
        serializer = PortfolioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=vendor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def certifications(self, request, pk=None):
        vendor = self.get_object()
        certifications = Certification.objects.filter(vendor=vendor)
        serializer = CertificationSerializer(certifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_certification(self, request, pk=None):
        vendor = self.get_object()
        serializer = CertificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=vendor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def education(self, request, pk=None):
        vendor = self.get_object()
        education = Education.objects.filter(vendor=vendor)
        serializer = EducationSerializer(education, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_education(self, request, pk=None):
        vendor = self.get_object()
        serializer = EducationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=vendor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
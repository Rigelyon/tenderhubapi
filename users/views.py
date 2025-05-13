from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .permissions import IsProfileOwnerOrReadOnly

from .models import (
    User, ClientProfile, VendorProfile, Portfolio, 
    Certification, Education, Review, Skill
)
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, ClientProfileSerializer,
    VendorProfileSerializer, PortfolioSerializer, CertificationSerializer,
    EducationSerializer, ReviewSerializer, SkillSerializer, OtherUserProfileSerializer
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

class OtherUserProfileView(generics.RetrieveAPIView):
    """
    API view to retrieve another user's profile information
    """
    serializer_class = OtherUserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(User, id=user_id)

class ClientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(ClientProfile, user=self.request.user)

class OtherClientProfileView(generics.RetrieveAPIView):
    """
    API view to retrieve another client's profile information
    """
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id, is_client=True)
        return get_object_or_404(ClientProfile, user=user)

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
    
    @action(detail=True, methods=['delete'])
    def delete_portfolio(self, request, pk=None):
        vendor = self.get_object()
        portfolio_id = request.query_params.get('portfolio_id')
        
        if not portfolio_id:
            return Response(
                {"error": "portfolio_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id, vendor=vendor)
        except Portfolio.DoesNotExist:
            return Response(
                {"error": "Portfolio not found or you don't have permission to delete it"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        portfolio.delete()
        return Response(
            {"message": "Portfolio deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['get'])
    def skills(self, request, pk=None):
        vendor = self.get_object()
        skills = vendor.skills.all()
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_skill(self, request, pk=None):
        vendor = self.get_object()
        
        # Check if we're adding an existing skill or creating a new one
        skill_id = request.data.get('id')
        skill_name = request.data.get('name')
        
        if skill_id:
            try:
                skill = Skill.objects.get(id=skill_id)
                vendor.skills.add(skill)
                return Response(
                    {"message": f"Skill '{skill.name}' added successfully"}, 
                    status=status.HTTP_200_OK
                )
            except Skill.DoesNotExist:
                return Response(
                    {"error": "Skill not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        elif skill_name:
            # Get or create the skill
            skill, created = Skill.objects.get_or_create(name=skill_name)
            # Add the skill to the vendor's profile
            vendor.skills.add(skill)
            return Response(
                {"message": f"Skill '{skill.name}' added successfully", "created": created}, 
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Either 'id' or 'name' parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def delete_skill(self, request, pk=None):
        vendor = self.get_object()
        skill_id = request.query_params.get('skill_id')
        
        if not skill_id:
            return Response(
                {"error": "skill_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            skill = Skill.objects.get(id=skill_id)
            if skill not in vendor.skills.all():
                return Response(
                    {"error": "This skill is not associated with your profile"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            vendor.skills.remove(skill)
            return Response(
                {"message": f"Skill '{skill.name}' removed successfully"}, 
                status=status.HTTP_200_OK
            )
        except Skill.DoesNotExist:
            return Response(
                {"error": "Skill not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
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
    
    @action(detail=True, methods=['delete'])
    def delete_certification(self, request, pk=None):
        vendor = self.get_object()
        cert_id = request.query_params.get('certification_id')
        
        if not cert_id:
            return Response(
                {"error": "certification_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            certification = Certification.objects.get(id=cert_id, vendor=vendor)
        except Certification.DoesNotExist:
            return Response(
                {"error": "Certification not found or you don't have permission to delete it"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        certification.delete()
        return Response(
            {"message": "Certification deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
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
    
    @action(detail=True, methods=['delete'])
    def delete_education(self, request, pk=None):
        vendor = self.get_object()
        education_id = request.query_params.get('education_id')
        
        if not education_id:
            return Response(
                {"error": "education_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            education = Education.objects.get(id=education_id, vendor=vendor)
        except Education.DoesNotExist:
            return Response(
                {"error": "Education record not found or you don't have permission to delete it"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        education.delete()
        return Response(
            {"message": "Education record deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )

class OtherVendorProfileView(generics.RetrieveAPIView):
    """
    API view to retrieve another vendor's profile information
    """
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id, is_vendor=True)
        return get_object_or_404(VendorProfile, user=user)

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]  # For create, update, delete - we could add IsAdminUser here if needed
    
    def create(self, request, *args, **kwargs):
        # Check if skill with this name already exists
        name = request.data.get('name')
        if not name:
            return Response(
                {"error": "Skill name is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        existing_skill = Skill.objects.filter(name__iexact=name).first()
        if existing_skill:
            serializer = self.get_serializer(existing_skill)
            return Response(
                {"message": "Skill already exists", "skill": serializer.data},
                status=status.HTTP_200_OK
            )
            
        return super().create(request, *args, **kwargs)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
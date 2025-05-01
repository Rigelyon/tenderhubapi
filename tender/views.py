from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Tender, Comment, Bid, Project, Tag
from .serializers import (
    TenderSerializer, TenderDetailSerializer, CommentSerializer, 
    BidSerializer, ProjectSerializer, TagSerializer
)
from project_activity.models import ProjectActivity
from project_activity.serializers import ProjectActivitySerializer
from .permissions import IsClientOrReadOnly, IsVendorOrReadOnly, IsProjectParticipant

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

class TenderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsClientOrReadOnly]
    
    def get_queryset(self):
        # Filter based on status, tags, etc. if provided in query params
        queryset = Tender.objects.all()
        status = self.request.query_params.get('status')
        tag = self.request.query_params.get('tag')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if tag:
            queryset = queryset.filter(tags__name=tag)
            
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TenderDetailSerializer
        return TenderSerializer
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        tender = self.get_object()
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(tender=tender, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def place_bid(self, request, pk=None):
        tender = self.get_object()
        
        # Check if user is a vendor
        if not request.user.is_vendor:
            return Response({"error": "Only vendors can place bids"}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if tender is open
        if tender.status != 'open':
            return Response({"error": "Bids can only be placed on open tenders"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if vendor already placed a bid
        if Bid.objects.filter(tender=tender, vendor=request.user).exists():
            return Response({"error": "You already placed a bid on this tender"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BidSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tender=tender, vendor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsClientOrReadOnly])
    def accept_bid(self, request, pk=None):
        tender = self.get_object()
        bid_id = request.data.get('bid_id')
        
        # Ensure the tender belongs to the requesting user
        if tender.client != request.user:
            return Response({"error": "You can only accept bids on your own tenders"}, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure tender is still open
        if tender.status != 'open':
            return Response({"error": "Can only accept bids on open tenders"}, status=status.HTTP_400_BAD_REQUEST)
        
        bid = get_object_or_404(Bid, bid_id=bid_id, tender=tender)
        bid.status = 'accepted'
        bid.save()
        
        # Create a project
        project = Project.objects.create(
            tender=tender,
            client=tender.client,
            vendor=bid.vendor,
            agreed_amount=bid.amount,
            deadline=tender.deadline
        )
        
        # Change tender status
        tender.status = 'in_progress'
        tender.save()
        
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

class BidViewSet(viewsets.ModelViewSet):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, IsVendorOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        
        # Vendors can only see their own bids
        if user.is_vendor:
            return Bid.objects.filter(vendor=user)
        
        # Clients can see all bids on their tenders
        if user.is_client:
            return Bid.objects.filter(tender__client=user)
        
        return Bid.objects.none()
    
    def perform_create(self, serializer):
        tender_id = self.request.data.get('tender')
        tender = get_object_or_404(Tender, tender_id=tender_id)
        serializer.save(tender=tender, vendor=self.request.user)

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectParticipant]
    
    def get_queryset(self):
        user = self.request.user
        # Users can see projects where they are either the client or the vendor
        return Project.objects.filter(Q(client=user) | Q(vendor=user))
    
    @action(detail=True, methods=['post'])
    def request_revision(self, request, pk=None):
        project = self.get_object()
        
        # Only clients can request revisions
        if request.user != project.client:
            return Response({"error": "Only clients can request revisions"}, status=status.HTTP_403_FORBIDDEN)
        
        if project.status != 'in_progress':
            return Response({"error": "Revisions can only be requested for in-progress projects"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Update project status
        project.status = 'revision_requested'
        project.save()
        
        # Record activity
        activity = ProjectActivity.objects.create(
            project=project,
            user=request.user,
            activity_type='revision_request',
            description=request.data.get('description', 'Revision requested')
        )
        
        return Response(ProjectActivitySerializer(activity).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def deliver_project(self, request, pk=None):
        project = self.get_object()
        
        # Only vendors can deliver projects
        if request.user != project.vendor:
            return Response({"error": "Only vendors can deliver projects"}, status=status.HTTP_403_FORBIDDEN)
        
        # Create delivery activity
        activity = ProjectActivity.objects.create(
            project=project,
            user=request.user,
            activity_type='delivery',
            description=request.data.get('description', 'Project delivered'),
            attachment=request.FILES.get('attachment')
        )
        
        return Response(ProjectActivitySerializer(activity).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def complete_project(self, request, pk=None):
        project = self.get_object()
        
        # Only clients can complete projects
        if request.user != project.client:
            return Response({"error": "Only clients can complete projects"}, status=status.HTTP_403_FORBIDDEN)
        
        # Update project status
        project.status = 'completed'
        project.save()
        
        # Update tender status
        project.tender.status = 'completed'
        project.tender.save()
        
        # Record activity
        activity = ProjectActivity.objects.create(
            project=project,
            user=request.user,
            activity_type='project_completion',
            description=request.data.get('description', 'Project marked as completed')
        )
        
        return Response(ProjectSerializer(project).data)
    
    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        project = self.get_object()
        new_price = request.data.get('new_price')
        
        if not new_price:
            return Response({"error": "New price is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Record old price
        old_price = project.agreed_amount
        
        # Update price
        project.agreed_amount = new_price
        project.save()
        
        # Record activity
        activity = ProjectActivity.objects.create(
            project=project,
            user=request.user,
            activity_type='price_change',
            description=f"Price updated from {old_price} to {new_price}",
            old_price=old_price,
            new_price=new_price
        )
        
        return Response(ProjectSerializer(project).data)
    
    @action(detail=True, methods=['post'])
    def update_deadline(self, request, pk=None):
        project = self.get_object()
        new_deadline = request.data.get('new_deadline')
        
        if not new_deadline:
            return Response({"error": "New deadline is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Record old deadline
        old_deadline = project.deadline
        
        # Update deadline
        project.deadline = new_deadline
        project.save()
        
        # Record activity
        activity = ProjectActivity.objects.create(
            project=project,
            user=request.user,
            activity_type='deadline_change',
            description=f"Deadline updated from {old_deadline} to {new_deadline}",
            old_deadline=old_deadline,
            new_deadline=new_deadline
        )
        
        return Response(ProjectSerializer(project).data)

class ProjectActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectActivitySerializer
    permission_classes = [IsAuthenticated, IsProjectParticipant]
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            project = get_object_or_404(Project, project_id=project_id)
            if project.client == self.request.user or project.vendor == self.request.user:
                return ProjectActivity.objects.filter(project=project)
        return ProjectActivity.objects.none()
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = get_object_or_404(Project, project_id=project_id)
        
        # Check if user is part of this project
        if project.client != self.request.user and project.vendor != self.request.user:
            raise permissions.PermissionDenied("You're not part of this project")
        
        serializer.save(project=project, user=self.request.user)
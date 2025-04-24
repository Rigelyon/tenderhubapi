from rest_framework import serializers

from project_activity.models import ProjectActivity
from .models import Bid, Project, Tag, Tender, Comment

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class BidSerializer(serializers.ModelSerializer):
    vendor_name = serializers.ReadOnlyField(source='vendor.username')
    vendor_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = Bid
        fields = ['bid_id', 'tender', 'vendor', 'vendor_name', 'vendor_profile', 
                  'amount', 'proposal', 'delivery_time', 'created_at', 'status']
        read_only_fields = ['tender', 'vendor', 'status']
    
    def get_vendor_profile(self, obj):
        return {
            'id': obj.vendor.id,
            'username': obj.vendor.username,
            'profile_picture': obj.vendor.profile_picture.url if obj.vendor.profile_picture else None,
        }
    
class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    user_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['comment_id', 'tender', 'user', 'user_name', 'user_picture', 'content', 'created_at']
        read_only_fields = ['tender', 'user']
    
    def get_user_picture(self, obj):
        return obj.user.profile_picture.url if obj.user.profile_picture else None

class TenderSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.username')
    client_picture = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, required=False)
    bid_count = serializers.ReadOnlyField()

    class Meta:
        model = Tender
        fields = [
            'tender_id', 'client', 'client_name', 'client_picture', 'title', 
            'description', 'attachment', 'max_duration', 'min_budget', 
            'max_budget', 'created_at', 'deadline', 'status', 'tags', 'bid_count'
        ]
        read_only_fields = ['client', 'created_at', 'status']

    def get_client_picture(self, obj):
        return obj.client.profile_picture.url if obj.client.profile_picture else None
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        tender = Tender.objects.create(**validated_data)
        
        # Handle tags
        for tag_data in tags_data:
            tag_name = tag_data.get('name')
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tender.tags.add(tag)
        
        return tender
    
class TenderDetailSerializer(TenderSerializer):
    bids = BidSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta(TenderSerializer.Meta):
        fields = TenderSerializer.Meta.fields + ['bids', 'comments']


class ProjectSerializer(serializers.ModelSerializer):
    tender_title = serializers.ReadOnlyField(source='tender.title')
    client_name = serializers.ReadOnlyField(source='client.username')
    vendor_name = serializers.ReadOnlyField(source='vendor.username')
    client_profile = serializers.SerializerMethodField()
    vendor_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'project_id', 'tender', 'tender_title', 'client', 'client_name',
            'client_profile', 'vendor', 'vendor_name', 'vendor_profile',
            'agreed_amount', 'start_date', 'deadline', 'status'
        ]
        read_only_fields = ['tender', 'client', 'vendor', 'agreed_amount', 'start_date']
    
    def get_client_profile(self, obj):
        return {
            'id': obj.client.id,
            'username': obj.client.username,
            'profile_picture': obj.client.profile_picture.url if obj.client.profile_picture else None,
        }
    
    def get_vendor_profile(self, obj):
        return {
            'id': obj.vendor.id,
            'username': obj.vendor.username,
            'profile_picture': obj.vendor.profile_picture.url if obj.vendor.profile_picture else None,
        }

class ProjectActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    user_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectActivity
        fields = [
            'activity_id', 'project', 'user', 'user_name', 'user_picture',
            'activity_type', 'description', 'created_at', 'attachment',
            'old_price', 'new_price', 'old_deadline', 'new_deadline'
        ]
        read_only_fields = ['project', 'user', 'created_at']
    
    def get_user_picture(self, obj):
        return obj.user.profile_picture.url if obj.user.profile_picture else None
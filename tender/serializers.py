from rest_framework import serializers

from project_activity.models import ProjectActivity
from .models import Bid, Project, Tag, Tender, Comment, Category

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

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
    user_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['comment_id', 'tender', 'user', 'user_name', 'user_picture', 'user_type', 'content', 'created_at']
        read_only_fields = ['tender', 'user']
    
    def get_user_picture(self, obj):
        return obj.user.profile_picture.url if obj.user.profile_picture else None
    
    def get_user_type(self, obj):
        if obj.user.is_client and obj.user.is_vendor:
            return "both"
        elif obj.user.is_client:
            return "client"
        elif obj.user.is_vendor:
            return "vendor"
        else:
            return "undefined"

class TenderSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.username')
    client_picture = serializers.SerializerMethodField()
    tags = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        write_only=True,
        required=False
    )
    tags_data = TagSerializer(many=True, read_only=True, source='tags')
    bid_count = serializers.ReadOnlyField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    tender_category_id = serializers.IntegerField(source='category.id', read_only=True)

    class Meta:
        model = Tender
        fields = [
            'tender_id', 'client', 'client_name', 'client_picture', 'title', 
            'description', 'attachment', 'max_duration', 'min_budget', 
            'max_budget', 'created_at', 'deadline', 'status', 'tags', 'tags_data', 'bid_count',
            'category', 'category_id', 'tender_category_id'
        ]
        read_only_fields = ['client', 'created_at', 'status']

    def get_client_picture(self, obj):
        return obj.client.profile_picture.url if obj.client.profile_picture else None
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        category = validated_data.pop('category', None)
        tender = Tender.objects.create(**validated_data)
        
        # Handle tags
        for tag_data in tags_data:
            if isinstance(tag_data, dict) and 'name' in tag_data:
                tag_name = tag_data.get('name')
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    tender.tags.add(tag)
            elif isinstance(tag_data, str):
                tag, _ = Tag.objects.get_or_create(name=tag_data)
                tender.tags.add(tag)
        
        if category:
            tender.category = category
            tender.save()
        
        return tender
        
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        category = validated_data.pop('category', None)
        
        # Update tender fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update category jika ada
        if category:
            instance.category = category
        
        # Update tags jika disediakan
        if tags_data is not None:
            # Hapus semua tags yang ada sebelumnya
            instance.tags.clear()
            
            # Tambahkan tags baru
            for tag_data in tags_data:
                if isinstance(tag_data, dict) and 'name' in tag_data:
                    tag_name = tag_data.get('name')
                    if tag_name:
                        tag, _ = Tag.objects.get_or_create(name=tag_name)
                        instance.tags.add(tag)
                elif isinstance(tag_data, str):
                    tag, _ = Tag.objects.get_or_create(name=tag_data)
                    instance.tags.add(tag)
        
        instance.save()
        return instance
    
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
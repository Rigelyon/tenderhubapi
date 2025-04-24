from rest_framework import serializers
from .models import ProjectActivity

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
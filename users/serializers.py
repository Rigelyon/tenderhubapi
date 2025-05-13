from rest_framework import serializers
from .models import User, ClientProfile, VendorProfile, Portfolio, Certification, Education, Review, Skill
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    user_type = serializers.ChoiceField(choices=[('client', 'client'), ('vendor', 'vendor')], write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'user_type')
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        
        # Set user type
        if user_type == 'client':
            user.is_client = True
            user.save()
            ClientProfile.objects.create(user=user)
        else:
            user.is_vendor = True
            user.save()
            VendorProfile.objects.create(user=user)
            
        return user

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'
        read_only_fields = ['vendor']

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'
        read_only_fields = ['vendor']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ['vendor']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.ReadOnlyField(source='reviewer.username')
    
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewer_name', 'reviewee', 'rating', 'comment', 'created_at', 'project']
        read_only_fields = ['reviewer']

class ClientProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientProfile
        fields = ['user', 'company_name', 'contact_number', 'address', 'reviews']
    
    def get_reviews(self, obj):
        reviews = Review.objects.filter(reviewee=obj.user)
        return ReviewSerializer(reviews, many=True).data

class VendorProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True,
        queryset=Skill.objects.all(),
        required=False,
        source='skills'
    )
    portfolios = PortfolioSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = VendorProfile
        fields = ['id', 'user', 'skills', 'skill_ids', 'hourly_rate', 'portfolios', 'certifications', 'education', 'reviews', 'average_rating']
    
    def get_reviews(self, obj):
        reviews = Review.objects.filter(reviewee=obj.user)
        return ReviewSerializer(reviews, many=True).data
    
    def get_average_rating(self, obj):
        reviews = Review.objects.filter(reviewee=obj.user)
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 0

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'bio', 
                  'location', 'language', 'is_client', 'is_vendor']
        read_only_fields = ['id', 'email', 'is_client', 'is_vendor']
        
class OtherUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving other users' profile data with limited fields
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'bio', 
                  'location', 'language', 'is_client', 'is_vendor']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'bio', 
                          'location', 'language', 'is_client', 'is_vendor']
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django.utils import timezone
from django.db.models import Avg, Count

from .models import (
    User, ClientProfile, VendorProfile, Skill, 
    Portfolio, Certification, Education, Review
)

# Custom admin actions
def make_client(modeladmin, request, queryset):
    queryset.update(is_client=True)
make_client.short_description = "Mark selected users as clients"

def make_vendor(modeladmin, request, queryset):
    queryset.update(is_vendor=True)
make_vendor.short_description = "Mark selected users as vendors"

def reset_user_type(modeladmin, request, queryset):
    queryset.update(is_client=False, is_vendor=False)
reset_user_type.short_description = "Reset user type (remove client/vendor status)"

# Inline admin classes
class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    extra = 0
    can_delete = False
    verbose_name_plural = "Client Profile"

class VendorProfileInline(admin.StackedInline):
    model = VendorProfile
    extra = 0
    can_delete = False
    filter_horizontal = ('skills',)
    verbose_name_plural = "Vendor Profile"

class PortfolioInline(admin.TabularInline):
    model = Portfolio
    extra = 0
    fields = ('title', 'description', 'link', 'date_created', 'image')
    classes = ('collapse',)

class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0
    fields = ('title', 'issuing_organization', 'issue_date', 'expiry_date', 'credential_id')
    classes = ('collapse',)

class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    fields = ('institution', 'degree', 'field_of_study', 'start_date', 'end_date')
    classes = ('collapse',)

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('reviewer', 'reviewee', 'rating', 'comment', 'project', 'created_at')
    readonly_fields = ('created_at',)
    fk_name = 'reviewee'
    verbose_name_plural = "Reviews Received"
    classes = ('collapse',)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'user_type', 'profile_picture_thumbnail', 'date_joined', 'last_login', 'is_active', 'is_staff')
    list_filter = ('is_client', 'is_vendor', 'is_staff', 'is_active', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('profile_picture', 'bio', 'location', 'language', 'is_client', 'is_vendor')
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'location')
    actions = [make_client, make_vendor, reset_user_type]
    list_per_page = 20
    save_on_top = True
    ordering = ('-date_joined',)
    
    def get_inlines(self, request, obj=None):
        if obj:
            inlines = []
            if obj.is_client:
                inlines.append(ClientProfileInline)
            if obj.is_vendor:
                inlines.append(VendorProfileInline)
                inlines.extend([PortfolioInline, CertificationInline, EducationInline])
            inlines.append(ReviewInline)
            return inlines
        return []
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'
    
    def user_type(self, obj):
        if obj.is_client and obj.is_vendor:
            return format_html('<span style="background-color: purple; color: white; padding: 3px 8px; border-radius: 10px;">Client & Vendor</span>')
        elif obj.is_client:
            return format_html('<span style="background-color: blue; color: white; padding: 3px 8px; border-radius: 10px;">Client</span>')
        elif obj.is_vendor:
            return format_html('<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 10px;">Vendor</span>')
        else:
            return format_html('<span style="background-color: gray; color: white; padding: 3px 8px; border-radius: 10px;">Undefined</span>')
    user_type.short_description = 'User Type'
    
    def profile_picture_thumbnail(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture.url)
        return format_html('<span style="color: #999;">No Image</span>')
    profile_picture_thumbnail.short_description = 'Profile Picture'

class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'company_name', 'contact_number', 'address_preview', 'project_count')
    list_filter = ('user__is_active',)
    search_fields = ('company_name', 'user__username', 'user__email', 'contact_number', 'address')
    raw_id_fields = ('user',)
    readonly_fields = ('project_count', 'get_client_reviews')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'company_name', 'contact_number', 'address')
        }),
        ('Statistics', {
            'fields': ('project_count', 'get_client_reviews'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def address_preview(self, obj):
        if len(obj.address) > 50:
            return f"{obj.address[:50]}..."
        return obj.address
    address_preview.short_description = 'Address'
    
    def project_count(self, obj):
        return obj.user.client_projects.count()
    project_count.short_description = 'Projects'
    
    def get_client_reviews(self, obj):
        reviews = Review.objects.filter(reviewee=obj.user)
        if not reviews.exists():
            return "No reviews yet"
        
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        html = f'<p><strong>Average Rating:</strong> {avg_rating:.1f}/5.0 from {reviews.count()} reviews</p>'
        html += '<ul style="padding-left: 20px;">'
        
        for review in reviews.order_by('-created_at')[:5]:
            html += f'''
            <li style="margin-bottom: 10px;">
                <div><strong>{review.reviewer.username}</strong> rated <strong>{review.rating}/5</strong> on {review.created_at.strftime('%Y-%m-%d')}</div>
                <div style="color: #555;">{review.comment[:100]}{"..." if len(review.comment) > 100 else ""}</div>
            </li>
            '''
        html += '</ul>'
        
        if reviews.count() > 5:
            html += f'<p>Showing 5 of {reviews.count()} reviews</p>'
            
        return mark_safe(html)
    get_client_reviews.short_description = 'Client Reviews'

class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'hourly_rate', 'skill_list', 'portfolio_count', 'avg_rating')
    search_fields = ('user__username', 'user__email', 'skills__name')
    filter_horizontal = ('skills',)
    raw_id_fields = ('user',)
    list_filter = ('skills', 'user__is_active')
    readonly_fields = ('portfolio_count', 'cert_count', 'education_count', 'avg_rating', 'get_vendor_reviews')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'hourly_rate', 'skills')
        }),
        ('Statistics', {
            'fields': ('portfolio_count', 'cert_count', 'education_count', 'avg_rating', 'get_vendor_reviews'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PortfolioInline, CertificationInline, EducationInline]
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def skill_list(self, obj):
        return ", ".join([skill.name for skill in obj.skills.all()[:5]])
    skill_list.short_description = 'Skills'
    
    def portfolio_count(self, obj):
        return obj.portfolios.count()
    portfolio_count.short_description = 'Portfolios'
    
    def cert_count(self, obj):
        return obj.certifications.count()
    cert_count.short_description = 'Certifications'
    
    def education_count(self, obj):
        return obj.education.count()
    education_count.short_description = 'Education Entries'
    
    def avg_rating(self, obj):
        reviews = Review.objects.filter(reviewee=obj.user)
        if not reviews.exists():
            return 'No ratings yet'
        avg = reviews.aggregate(Avg('rating'))['rating__avg']
        return f'{avg:.1f}/5.0 ({reviews.count()} reviews)'
    avg_rating.short_description = 'Average Rating'
    
    def get_vendor_reviews(self, obj):
        reviews = Review.objects.filter(reviewee=obj.user)
        if not reviews.exists():
            return "No reviews yet"
        
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        html = f'<p><strong>Average Rating:</strong> {avg_rating:.1f}/5.0 from {reviews.count()} reviews</p>'
        html += '<ul style="padding-left: 20px;">'
        
        for review in reviews.order_by('-created_at')[:5]:
            html += f'''
            <li style="margin-bottom: 10px;">
                <div><strong>{review.reviewer.username}</strong> rated <strong>{review.rating}/5</strong> on {review.created_at.strftime('%Y-%m-%d')}</div>
                <div style="color: #555;">{review.comment[:100]}{"..." if len(review.comment) > 100 else ""}</div>
            </li>
            '''
        html += '</ul>'
        
        if reviews.count() > 5:
            html += f'<p>Showing 5 of {reviews.count()} reviews</p>'
            
        return mark_safe(html)
    get_vendor_reviews.short_description = 'Vendor Reviews'

class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor_count')
    search_fields = ('name',)
    
    def vendor_count(self, obj):
        return obj.vendorprofile_set.count()
    vendor_count.short_description = 'Vendors with this skill'

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor_link', 'date_created', 'has_image', 'has_link')
    list_filter = ('date_created', 'vendor__user__is_active')
    search_fields = ('title', 'description', 'vendor__user__username')
    raw_id_fields = ('vendor',)
    date_hierarchy = 'date_created'
    readonly_fields = ('image_preview',)
    
    fieldsets = (
        (None, {
            'fields': ('vendor', 'title', 'description', 'date_created')
        }),
        ('Media', {
            'fields': ('image', 'image_preview', 'link'),
            'classes': ('collapse',)
        }),
    )
    
    def vendor_link(self, obj):
        url = reverse('admin:users_vendorprofile_change', args=[obj.vendor.id])
        return format_html('<a href="{}">{}</a>', url, obj.vendor)
    vendor_link.short_description = 'Vendor'
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'
    
    def has_link(self, obj):
        return bool(obj.link)
    has_link.boolean = True
    has_link.short_description = 'Has Link'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image Preview'

class CertificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor_link', 'issuing_organization', 'issue_date', 'expiry_date', 'is_expired')
    list_filter = ('issue_date', 'expiry_date', 'issuing_organization')
    search_fields = ('title', 'issuing_organization', 'vendor__user__username', 'credential_id')
    raw_id_fields = ('vendor',)
    date_hierarchy = 'issue_date'
    
    def vendor_link(self, obj):
        url = reverse('admin:users_vendorprofile_change', args=[obj.vendor.id])
        return format_html('<a href="{}">{}</a>', url, obj.vendor)
    vendor_link.short_description = 'Vendor'
    
    def is_expired(self, obj):
        if not obj.expiry_date:
            return None
        is_expired = obj.expiry_date < timezone.localdate()
        return format_html(
            '<span style="color: {};">{}</span>',
            'red' if is_expired else 'green',
            'Expired' if is_expired else 'Valid'
        )
    is_expired.short_description = 'Status'

class EducationAdmin(admin.ModelAdmin):
    list_display = ('vendor_link', 'degree_field', 'institution', 'date_range', 'duration')
    list_filter = ('start_date', 'end_date', 'degree')
    search_fields = ('institution', 'degree', 'field_of_study', 'vendor__user__username')
    raw_id_fields = ('vendor',)
    date_hierarchy = 'start_date'
    
    def vendor_link(self, obj):
        url = reverse('admin:users_vendorprofile_change', args=[obj.vendor.id])
        return format_html('<a href="{}">{}</a>', url, obj.vendor)
    vendor_link.short_description = 'Vendor'
    
    def degree_field(self, obj):
        return f"{obj.degree} in {obj.field_of_study}"
    degree_field.short_description = 'Degree & Field'
    
    def date_range(self, obj):
        end = obj.end_date.strftime('%b %Y') if obj.end_date else "Present"
        return f"{obj.start_date.strftime('%b %Y')} - {end}"
    date_range.short_description = 'Period'
    
    def duration(self, obj):
        if not obj.end_date:
            end_date = timezone.localdate()
        else:
            end_date = obj.end_date
            
        delta = (end_date.year - obj.start_date.year) * 12 + (end_date.month - obj.start_date.month)
        years = delta // 12
        months = delta % 12
        
        if years and months:
            return f"{years} yr{'s' if years > 1 else ''}, {months} mo{'s' if months > 1 else ''}"
        elif years:
            return f"{years} yr{'s' if years > 1 else ''}"
        else:
            return f"{months} mo{'s' if months > 1 else ''}"
    duration.short_description = 'Duration'

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer_link', 'reviewee_link', 'star_rating', 'project_link', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'reviewer__username', 'reviewee__username', 'project__tender__title')
    raw_id_fields = ('reviewer', 'reviewee', 'project')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'comment_formatted')
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('reviewer', 'reviewee', 'rating', 'project', 'created_at')
        }),
        ('Review Content', {
            'fields': ('comment_formatted',)
        }),
    )
    
    def reviewer_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.reviewer.id])
        return format_html('<a href="{}">{}</a>', url, obj.reviewer.username)
    reviewer_link.short_description = 'Reviewer'
    
    def reviewee_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.reviewee.id])
        return format_html('<a href="{}">{}</a>', url, obj.reviewee.username)
    reviewee_link.short_description = 'Reviewee'
    
    def project_link(self, obj):
        url = reverse('admin:tender_project_change', args=[obj.project.project_id])
        return format_html('<a href="{}">{}</a>', url, obj.project)
    project_link.short_description = 'Project'
    
    def star_rating(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = "#FFD700" if obj.rating >= 4 else ("#FFA500" if obj.rating >= 3 else "#FF0000")
        return format_html('<span style="color: {};">{}</span>', color, stars)
    star_rating.short_description = 'Rating'
    
    def comment_formatted(self, obj):
        return mark_safe(f'<div style="max-width: 600px;">{obj.comment}</div>')
    comment_formatted.short_description = 'Comment'

# Register all models with their custom admin classes
admin.site.register(User, CustomUserAdmin)
admin.site.register(ClientProfile, ClientProfileAdmin)
admin.site.register(VendorProfile, VendorProfileAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Review, ReviewAdmin)

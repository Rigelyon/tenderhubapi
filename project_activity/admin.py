from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django.db.models import Q
from django import forms
from django.utils import timezone
import datetime

from .models import ProjectActivity

# Custom admin actions
def mark_as_important(modeladmin, request, queryset):
    """Custom action to add 'IMPORTANT: ' prefix to selected activities"""
    for activity in queryset:
        if not activity.description.startswith('IMPORTANT: '):
            activity.description = f"IMPORTANT: {activity.description}"
            activity.save()
mark_as_important.short_description = "Mark selected activities as important"

def download_all_attachments(modeladmin, request, queryset):
    """Create a page with links to all attachments from selected activities"""
    activities_with_attachments = queryset.exclude(attachment='')
    if not activities_with_attachments:
        modeladmin.message_user(request, "No attachments found in selected activities")
        return
    
    # In a real implementation, this would create a zip file or page with links
    # For demo purposes, we'll just show a message
    count = activities_with_attachments.count()
    modeladmin.message_user(request, f"Found {count} activities with attachments. In a real implementation, these would be downloaded or linked.")
download_all_attachments.short_description = "Download attachments from selected activities"

class ActivityTypeListFilter(admin.SimpleListFilter):
    title = 'activity category'
    parameter_name = 'activity_category'
    
    def lookups(self, request, model_admin):
        return (
            ('comment_attachment', 'Comments & Attachments'),
            ('price_deadline', 'Price & Deadline Changes'),
            ('project_status', 'Project Status Changes'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'comment_attachment':
            return queryset.filter(Q(activity_type='comment') | Q(activity_type='attachment'))
        if self.value() == 'price_deadline':
            return queryset.filter(Q(activity_type='price_change') | Q(activity_type='deadline_change'))
        if self.value() == 'project_status':
            return queryset.filter(Q(activity_type='delivery') | 
                                  Q(activity_type='revision_request') |
                                  Q(activity_type='project_completion'))
        return queryset

class RecentActivityFilter(admin.SimpleListFilter):
    title = 'time period'
    parameter_name = 'time_period'
    
    def lookups(self, request, model_admin):
        return (
            ('1d', 'Last 24 hours'),
            ('7d', 'Last 7 days'),
            ('30d', 'Last 30 days'),
            ('90d', 'Last 90 days'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == '1d':
            return queryset.filter(created_at__gte=timezone.now() - datetime.timedelta(days=1))
        if self.value() == '7d':
            return queryset.filter(created_at__gte=timezone.now() - datetime.timedelta(days=7))
        if self.value() == '30d':
            return queryset.filter(created_at__gte=timezone.now() - datetime.timedelta(days=30))
        if self.value() == '90d':
            return queryset.filter(created_at__gte=timezone.now() - datetime.timedelta(days=90))
        return queryset

class ProjectActivityAdminForm(forms.ModelForm):
    class Meta:
        model = ProjectActivity
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
        }

class ProjectActivityAdmin(admin.ModelAdmin):
    form = ProjectActivityAdminForm
    list_display = ('activity_id', 'activity_icon', 'project_link', 'user_link', 'activity_type', 'activity_summary', 'time_ago')
    list_filter = ('activity_type', ActivityTypeListFilter, RecentActivityFilter, 'created_at', 'user__is_client', 'user__is_vendor')
    search_fields = ('description', 'project__tender__title', 'user__username', 'project__client__username', 'project__vendor__username')
    readonly_fields = ('created_at', 'attachment_preview', 'price_change_display', 'deadline_change_display', 'user_detail')
    list_per_page = 25
    date_hierarchy = 'created_at'
    save_on_top = True
    actions = [mark_as_important, download_all_attachments]
    
    fieldsets = (
        (None, {
            'fields': ('project', 'user', 'user_detail', 'activity_type', 'description', 'created_at')
        }),
        ('Attachments', {
            'fields': ('attachment', 'attachment_preview'),
            'classes': ('collapse',)
        }),
        ('Price Changes', {
            'fields': ('old_price', 'new_price', 'price_change_display'),
            'classes': ('collapse',)
        }),
        ('Deadline Changes', {
            'fields': ('old_deadline', 'new_deadline', 'deadline_change_display'),
            'classes': ('collapse',)
        }),
    )
    
    def project_link(self, obj):
        url = reverse('admin:tender_project_change', args=[obj.project.project_id])
        title = obj.project.tender.title
        return format_html('<a href="{}">{}</a>', url, title[:40] + '...' if len(title) > 40 else title)
    project_link.short_description = 'Project'
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.id])
        user_type = ""
        if obj.user.is_client:
            user_type = " (Client)"
        elif obj.user.is_vendor:
            user_type = " (Vendor)"
        return format_html('<a href="{}">{}{}</a>', url, obj.user.username, user_type)
    user_link.short_description = 'User'
    
    def user_detail(self, obj):
        """Display detailed user information in read-only field"""
        user = obj.user
        html = f"""
        <div style="padding: 10px; background-color: #f9f9f9; border-radius: 5px; margin: 10px 0;">
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Full Name:</strong> {user.first_name} {user.last_name}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>User Type:</strong> {"Client" if user.is_client else "Vendor" if user.is_vendor else "Staff"}</p>
        </div>
        """
        return mark_safe(html)
    user_detail.short_description = "User Details"
    
    def activity_icon(self, obj):
        icons = {
            'comment': '💬',
            'attachment': '📎',
            'price_change': '💰',
            'deadline_change': '📅',
            'delivery': '📦',
            'revision_request': '🔄',
            'project_completion': '✅',
        }
        return icons.get(obj.activity_type, '❓')
    activity_icon.short_description = ''
    
    def activity_summary(self, obj):
        if len(obj.description) > 100:
            return obj.description[:100] + '...'
        return obj.description
    activity_summary.short_description = 'Summary'
    
    def time_ago(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days == 0:
            if diff.seconds < 60:
                return 'just now'
            if diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
            hours = diff.seconds // 3600
            return f'{hours} hour{"s" if hours > 1 else ""} ago'
        elif diff.days < 30:
            return f'{diff.days} day{"s" if diff.days > 1 else ""} ago'
        elif diff.days < 365:
            months = diff.days // 30
            return f'{months} month{"s" if months > 1 else ""} ago'
        else:
            years = diff.days // 365
            return f'{years} year{"s" if years > 1 else ""} ago'
    time_ago.short_description = 'Time'
    
    def attachment_preview(self, obj):
        if not obj.attachment:
            return "No attachment"
        
        file_url = obj.attachment.url
        file_name = obj.attachment.name.split('/')[-1]
        file_extension = file_name.split('.')[-1].lower()
        
        # Handle image files
        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-width: 300px; max-height: 200px;" /></a>', 
                              file_url, file_url)
        
        # Handle PDF files
        if file_extension == 'pdf':
            return format_html('<a href="{}" target="_blank" class="button" style="display: inline-block; padding: 5px 15px; background-color: #e74c3c; color: white; text-decoration: none; border-radius: 3px;"><i class="fas fa-file-pdf"></i> View PDF</a>', file_url)
        
        # Handle other file types
        file_icon = '📄'
        return format_html('<a href="{}" target="_blank">{} {}</a>', file_url, file_icon, file_name)
    attachment_preview.short_description = 'Attachment Preview'
    
    def price_change_display(self, obj):
        if not obj.old_price or not obj.new_price:
            return "No price change data"
        
        diff = float(obj.new_price) - float(obj.old_price)
        percent = (diff / float(obj.old_price)) * 100
        
        if diff > 0:
            color = 'green'
            symbol = '▲'
        else:
            color = 'red'
            symbol = '▼'
            
        return format_html(
            '<div style="font-size: 1.1em; margin: 10px 0;">'
            '  <div>Old price: <strong>${:,.2f}</strong></div>'
            '  <div>New price: <strong>${:,.2f}</strong></div>'
            '  <div style="margin-top: 5px; color: {};">'
            '    <strong>{} ${:,.2f} ({:.1f}%)</strong>'
            '  </div>'
            '</div>',
            float(obj.old_price), float(obj.new_price), color, symbol, abs(diff), abs(percent)
        )
    price_change_display.short_description = 'Price Change Analysis'
    
    def deadline_change_display(self, obj):
        if not obj.old_deadline or not obj.new_deadline:
            return "No deadline change data"
        
        days_diff = (obj.new_deadline - obj.old_deadline).days
        
        if days_diff > 0:
            color = 'green'
            message = f"Deadline extended by {days_diff} day{'s' if days_diff != 1 else ''}"
        elif days_diff < 0:
            color = 'red'
            message = f"Deadline shortened by {abs(days_diff)} day{'s' if abs(days_diff) != 1 else ''}"
        else:
            color = 'gray'
            message = "Deadline date changed but duration remains the same"
            
        return format_html(
            '<div style="font-size: 1.1em; margin: 10px 0;">'
            '  <div>Old deadline: <strong>{}</strong></div>'
            '  <div>New deadline: <strong>{}</strong></div>'
            '  <div style="margin-top: 5px; color: {};">'
            '    <strong>{}</strong>'
            '  </div>'
            '</div>',
            obj.old_deadline.strftime('%Y-%m-%d'), obj.new_deadline.strftime('%Y-%m-%d'), color, message
        )
    deadline_change_display.short_description = 'Deadline Change Analysis'
    
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css',)
        }

# Register the ProjectActivity model with the custom admin class
admin.site.register(ProjectActivity, ProjectActivityAdmin)

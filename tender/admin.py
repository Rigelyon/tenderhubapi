from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from .models import Tag, Tender, Category, Comment, Bid, Project

# Custom admin actions
def mark_tenders_completed(modeladmin, request, queryset):
    queryset.update(status='completed')
mark_tenders_completed.short_description = "Mark selected tenders as completed"

def mark_tenders_cancelled(modeladmin, request, queryset):
    queryset.update(status='cancelled')
mark_tenders_cancelled.short_description = "Mark selected tenders as cancelled"

def mark_bids_accepted(modeladmin, request, queryset):
    for bid in queryset:
        if bid.tender.status == 'open':
            bid.status = 'accepted'
            bid.save()
            
            # Create a project
            tender = bid.tender
            Project.objects.create(
                tender=tender,
                client=tender.client,
                vendor=bid.vendor,
                agreed_amount=bid.amount,
                deadline=tender.deadline
            )
            
            # Update tender status
            tender.status = 'in_progress'
            tender.save()
mark_bids_accepted.short_description = "Accept selected bids and create projects"

# Inline admin classes
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('user', 'content', 'created_at')

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('vendor', 'amount', 'delivery_time', 'status', 'created_at')

admin.site.site_header = "TenderHub Administration"
admin.site.site_title = "TenderHub"
admin.site.index_title = "TenderHub Platform Management"

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tenders_count')
    search_fields = ('name',)
    
    def get_tenders_count(self, obj):
        return obj.tenders.count()
    get_tenders_count.short_description = 'Tenders using this tag'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_tenders_count')
    search_fields = ('name', 'description')
    list_display_links = ('name',)
    
    def get_tenders_count(self, obj):
        return obj.tenders.count()
    get_tenders_count.short_description = 'Tenders in category'

class TenderAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'status', 'budget_range', 'deadline', 'created_at', 'bid_count', 'days_remaining', 'view_project_link')
    list_filter = ('status', 'created_at', 'category')
    search_fields = ('title', 'description', 'client__username')
    readonly_fields = ('created_at', 'bid_count')
    filter_horizontal = ('tags',)
    actions = [mark_tenders_completed, mark_tenders_cancelled]
    list_per_page = 20
    save_on_top = True
    inlines = [BidInline, CommentInline]
    
    fieldsets = (
        (None, {
            'fields': ('client', 'title', 'description', 'status', 'created_at')
        }),
        ('Budget & Timeline', {
            'fields': ('min_budget', 'max_budget', 'max_duration', 'deadline')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Attachments', {
            'fields': ('attachment',),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'
    
    def budget_range(self, obj):
        return f"${obj.min_budget} - ${obj.max_budget}"
    budget_range.short_description = 'Budget Range'
    
    def days_remaining(self, obj):
        if obj.status == 'open':
            remaining = (obj.deadline - timezone.localdate()).days
            if remaining < 0:
                return format_html('<span style="color: red;">Expired</span>')
            elif remaining < 3:
                return format_html('<span style="color: orange;">{} days</span>', remaining)
            else:
                return f"{remaining} days"
        return "-"
    days_remaining.short_description = 'Days Remaining'
    
    def view_project_link(self, obj):
        if hasattr(obj, 'project'):
            url = reverse('admin:tender_project_change', args=[obj.project.project_id])
            return format_html('<a href="{}">View Project</a>', url)
        return "-"
    view_project_link.short_description = 'Project'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'tender_link', 'user', 'truncated_content', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'tender__title', 'user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def tender_link(self, obj):
        url = reverse('admin:tender_tender_change', args=[obj.tender.tender_id])
        return format_html('<a href="{}">{}</a>', url, obj.tender.title)
    tender_link.short_description = 'Tender'
    
    def truncated_content(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    truncated_content.short_description = 'Content'

class BidAdmin(admin.ModelAdmin):
    list_display = ('bid_id', 'tender_link', 'vendor', 'amount', 'delivery_time', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('proposal', 'tender__title', 'vendor__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    actions = [mark_bids_accepted]
    
    def tender_link(self, obj):
        url = reverse('admin:tender_tender_change', args=[obj.tender.tender_id])
        return format_html('<a href="{}">{}</a>', url, obj.tender.title)
    tender_link.short_description = 'Tender'

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'tender_link', 'client', 'vendor', 'agreed_amount', 'deadline', 'status', 'days_since_start', 'completion_percentage')
    list_filter = ('status', 'start_date')
    search_fields = ('tender__title', 'client__username', 'vendor__username')
    readonly_fields = ('start_date', 'get_activity_history')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (None, {
            'fields': ('tender', 'client', 'vendor', 'status')
        }),
        ('Financial & Timeline', {
            'fields': ('agreed_amount', 'start_date', 'deadline')
        }),
        ('Project History', {
            'fields': ('get_activity_history',),
            'classes': ('collapse',)
        }),
    )
    
    def tender_link(self, obj):
        url = reverse('admin:tender_tender_change', args=[obj.tender.tender_id])
        return format_html('<a href="{}">{}</a>', url, obj.tender.title)
    tender_link.short_description = 'Tender'
    
    def days_since_start(self, obj):
        return (timezone.localdate() - obj.start_date).days
    days_since_start.short_description = 'Days Running'
    
    def completion_percentage(self, obj):
        if obj.status == 'completed':
            return format_html('<span style="color: green;">100%</span>')
        
        total_days = (obj.deadline - obj.start_date).days
        if total_days <= 0:
            return "N/A"
        
        days_passed = (timezone.localdate() - obj.start_date).days
        if days_passed < 0:
            return "0%"
        
        percentage = min(round((days_passed / total_days) * 100), 99)
        color = 'green' if percentage < 60 else ('orange' if percentage < 90 else 'red')
        return format_html('<span style="color: {};">{}%</span>', color, percentage)
    completion_percentage.short_description = 'Completion'
    
    def get_activity_history(self, obj):
        activities = obj.activities.all().order_by('-created_at')
        if not activities:
            return "No activities recorded"
        
        html = '<ul style="list-style-type: none; padding-left: 0;">'
        for activity in activities:
            html += f'<li style="margin-bottom: 10px;"><b>{activity.created_at.strftime("%Y-%m-%d %H:%M")}</b>: <b>{activity.activity_type}</b> by <b>{activity.user.username}</b><br/>{activity.description}</li>'
        html += '</ul>'
        return mark_safe(html)
    get_activity_history.short_description = 'Activity History'

# Register all models with their custom admin classes
admin.site.register(Tag, TagAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tender, TenderAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Project, ProjectAdmin)

# Register the many-to-many through model
admin.site.register(Tender.tags.through)
search_fields = ('name', 'description')

class TenderAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'status', 'min_budget', 'max_budget', 'deadline', 'created_at', 'bid_count')
    list_filter = ('status', 'created_at', 'category')
    search_fields = ('title', 'description', 'client__username')
    readonly_fields = ('created_at',)
    filter_horizontal = ('tags',)
    fieldsets = (
        (None, {
            'fields': ('client', 'title', 'description', 'status', 'created_at')
        }),
        ('Budget & Timeline', {
            'fields': ('min_budget', 'max_budget', 'max_duration', 'deadline')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Attachments', {
            'fields': ('attachment',),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'tender', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'tender__title', 'user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

class BidAdmin(admin.ModelAdmin):
    list_display = ('bid_id', 'tender', 'vendor', 'amount', 'delivery_time', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('proposal', 'tender__title', 'vendor__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'tender', 'client', 'vendor', 'agreed_amount', 'deadline', 'status', 'start_date')
    list_filter = ('status', 'start_date')
    search_fields = ('tender__title', 'client__username', 'vendor__username')
    readonly_fields = ('start_date',)
    date_hierarchy = 'start_date'
    fieldsets = (
        (None, {
            'fields': ('tender', 'client', 'vendor', 'status')
        }),
        ('Financial & Timeline', {
            'fields': ('agreed_amount', 'start_date', 'deadline')
        }),
    )
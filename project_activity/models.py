from django.db import models

from tender.models import Project
from users.models import User

class ProjectActivity(models.Model):
    ACTIVITY_TYPE_CHOICES = (
        ('comment', 'Comment'),
        ('attachment', 'Attachment'),
        ('price_change', 'Price Change'),
        ('deadline_change', 'Deadline Change'),
        ('delivery', 'Delivery'),
        ('revision_request', 'Revision Request'),
        ('project_completion', 'Project Completion'),
    )

    activity_id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='project_attachments/', blank=True, null=True)

    # For price change
    old_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    new_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    
    # For deadline change
    old_deadline = models.DateField(null=True, blank=True)
    new_deadline = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Project Activity"
        verbose_name_plural = "Project Activities"
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.activity_type} on {self.project}"

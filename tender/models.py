from django.utils import timezone
from django.db import models

from users.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Tender(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    tender_id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenders')
    title = models.CharField(verbose_name="Title", max_length=255)
    description = models.TextField(verbose_name="Description")
    attachment = models.FileField(upload_to='tender_attachments/', blank=True, null=True)
    max_duration = models.IntegerField(verbose_name="Max duration (days)")
    min_budget = models.DecimalField(verbose_name="Min budget", decimal_places=2, max_digits=10)
    max_budget = models.DecimalField(verbose_name="Max budget", decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(verbose_name="Date created", default=timezone.now)
    deadline = models.DateField(verbose_name="Deadline")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    tags = models.ManyToManyField(Tag, related_name='tenders', blank=True)

    class Meta:
        verbose_name = "Tender"
        verbose_name_plural = "Tenders"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def bid_count(self):
        return self.bids.count()
    
    @property
    def top_bid(self):
        top_bid = self.bids.order_by('amount').first()
        return top_bid
    
class Comment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tender_comments')
    content = models.TextField(verbose_name="Content")
    created_at = models.DateTimeField(verbose_name="Date created", default=timezone.now)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user} on {self.tender.title}"
    
class Bid(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    bid_id = models.BigAutoField(primary_key=True)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='bids')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    proposal = models.TextField()
    delivery_time = models.IntegerField(help_text="Delivery time in days")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        verbose_name = "Bid"
        verbose_name_plural = "Bids"
        ordering = ['amount']
    
    def __str__(self):
        return f"Bid by {self.vendor.username} on {self.tender.title}"
    
class Project(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('revision_requested', 'Revision Requested'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    project_id = models.BigAutoField(primary_key=True)
    tender = models.OneToOneField(Tender, on_delete=models.CASCADE, related_name='project')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_projects')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_projects')
    agreed_amount = models.DecimalField(decimal_places=2, max_digits=10)
    start_date = models.DateField(auto_now_add=True)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Project: {self.tender.title}"
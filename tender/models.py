from django.utils import timezone
from django.db import models

class Tender(models.Model):
    tender_id = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name="Title", max_length=255)
    description = models.TextField(verbose_name="Description")
    attachment = models.CharField(verbose_name="Attachment")
    max_duration = models.IntegerField(verbose_name="Max duration")
    min_budget = models.DecimalField(verbose_name="Min budget", decimal_places=2, max_digits=10)
    max_budget = models.DecimalField(verbose_name="Max budget", decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(verbose_name="Date created", default=timezone.now)
    deadline = models.DateField(verbose_name="Deadline")
    status = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Tender"
        verbose_name_plural = "Tenders"
        ordering = ['created_at']
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE)
    user = models.CharField(max_length=255)
    content = models.TextField(verbose_name="Content")
    created_at = models.DateTimeField(verbose_name="Date created", default=timezone.now)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user} on {self.tender.title}"
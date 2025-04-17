from django.db import models

class ProjectActivity(models.Model):
    activity_id = models.BigAutoField(primary_key=True)
    project_id = models.BigIntegerField()
    activity_name = models.CharField(max_length=255)
    activity_description = models.TextField()
    activity_start_date = models.DateField()
    activity_end_date = models.DateField()
    activity_status = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = "Project Activity"
        verbose_name_plural = "Project Activities"
        ordering = ['activity_start_date']
        
    def __str__(self):
        return self.activity_name

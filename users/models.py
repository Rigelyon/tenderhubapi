from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model that extends the AbstractUser model.
    """
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=10, blank=True)

    is_client = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['username']
        
    def __str__(self):
        return self.username
    
class ClientProfile(models.Model):
    """
    Model to store client profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    address = models.TextField()

    class Meta:
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"
        
    def __str__(self):
        return self.company_name
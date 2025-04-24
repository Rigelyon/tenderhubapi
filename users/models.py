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
    
class VendorProfile(models.Model):
    """
    Model to store vendor profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    skills = models.ManyToManyField('Skill', blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = "Vendor Profile"
        verbose_name_plural = "Vendor Profiles"
        
    def __str__(self):
        return f"{self.user.username}'s vendor profile"

class Skill(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Portfolio(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='portfolios')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio_images', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    date_created = models.DateField()
    
    def __str__(self):
        return self.title

class Certification(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.title

class Education(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} from {self.institution}"

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Below Average'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    )
    
    # Can be from client to vendor or vendor to client
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey('tender.Project', on_delete=models.CASCADE, related_name='reviews')
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username}"
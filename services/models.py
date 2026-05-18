from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


class ServiceType(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=50, default='🔧')
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Service Type'
        verbose_name_plural = 'Service Types'
        ordering            = ['name']

    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    STATUS_CHOICES = [
        ('active',    'Active'),
        ('inactive',  'Inactive'),
        ('suspended', 'Suspended'),
        ('pending',   'Pending Approval'),
    ]

    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    service_types = models.ManyToManyField(ServiceType, related_name='providers')
    phone         = models.CharField(max_length=20)
    email         = models.EmailField()
    address       = models.TextField()
    city          = models.CharField(max_length=100)
    state         = models.CharField(max_length=100)
    pincode       = models.CharField(max_length=10)
    latitude      = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    opening_time  = models.TimeField(null=True, blank=True)
    closing_time  = models.TimeField(null=True, blank=True)
    is_24_7       = models.BooleanField(default=False)
    base_fee      = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_available  = models.BooleanField(default=True)
    logo          = models.ImageField(upload_to='providers/logos/', blank=True, null=True)
    rating        = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    total_jobs    = models.PositiveIntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Service Provider'
        verbose_name_plural = 'Service Providers'
        ordering            = ['-rating', 'business_name']

    def __str__(self):
        return f"{self.business_name} ({self.city})"

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            self.rating       = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.total_reviews= reviews.count()
            self.save(update_fields=['rating', 'total_reviews'])


class Review(models.Model):
    provider   = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating     = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment    = models.TextField(blank=True)
    is_approved= models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Review'
        verbose_name_plural = 'Reviews'
        ordering            = ['-created_at']
        unique_together     = ['provider', 'user']

    def __str__(self):
        return f"{self.user.email} → {self.provider.business_name} ({self.rating}★)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.provider.update_rating()

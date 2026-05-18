from django.db import models
from accounts.models import User
from services.models import ServiceProvider


class EmergencyRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('assigned',    'Provider Assigned'),
        ('en_route',    'Technician En Route'),
        ('in_progress', 'Service In Progress'),
        ('completed',   'Completed'),
        ('cancelled',   'Cancelled'),
    ]
    VEHICLE_CHOICES = [
        ('car',        'Car / Sedan'),
        ('suv',        'SUV / MUV'),
        ('motorcycle', 'Motorcycle'),
        ('truck',      'Truck / Commercial'),
        ('other',      'Other'),
    ]
    ISSUE_CHOICES = [
        ('flat_tyre',      'Flat Tyre'),
        ('engine_failure', 'Engine Failure'),
        ('battery_dead',   'Battery Dead'),
        ('accident',       'Accident'),
        ('out_of_fuel',    'Out of Fuel'),
        ('overheating',    'Overheating'),
        ('electrical',     'Electrical Issue'),
        ('other',          'Other'),
    ]
    PRIORITY_CHOICES = [
        ('low',      'Low'),
        ('medium',   'Medium'),
        ('high',     'High'),
        ('critical', 'Critical'),
    ]

    user              = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='emergency_requests')
    requester_name    = models.CharField(max_length=150)
    requester_phone   = models.CharField(max_length=20)
    vehicle_type      = models.CharField(max_length=20, choices=VEHICLE_CHOICES, default='car')
    issue_type        = models.CharField(max_length=30, choices=ISSUE_CHOICES,   default='other')
    notes             = models.TextField(blank=True)
    location_address  = models.TextField()
    latitude          = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude         = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    assigned_provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, null=True, blank=True, related_name='emergency_assignments')
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES,   default='pending')
    priority          = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)
    assigned_at       = models.DateTimeField(null=True, blank=True)
    completed_at      = models.DateTimeField(null=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Emergency Request'
        verbose_name_plural = 'Emergency Requests'
        ordering            = ['-created_at']

    def __str__(self):
        return f"#{self.pk} — {self.requester_name} ({self.get_issue_type_display()}) [{self.get_status_display()}]"


class Dispatch(models.Model):
    request          = models.OneToOneField(EmergencyRequest, on_delete=models.CASCADE, related_name='dispatch')
    technician_name  = models.CharField(max_length=150)
    technician_phone = models.CharField(max_length=20)
    vehicle_number   = models.CharField(max_length=20, blank=True)
    dispatched_at    = models.DateTimeField(auto_now_add=True)
    notes            = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Dispatch'
        verbose_name_plural = 'Dispatches'

    def __str__(self):
        return f"Dispatch #{self.request.pk} — {self.technician_name}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
    ]
    request        = models.OneToOneField(EmergencyRequest, on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    service_request = models.OneToOneField('ServiceRequest', on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        ref = f"Req #{self.request.pk}" if self.request else f"SR #{self.service_request.pk}"
        return f"Payment #{self.pk} for {ref} - {self.amount} INR [{self.get_status_display()}]"


class ServiceRequest(models.Model):
    """Non-emergency, customer-initiated service request directed at a specific provider."""

    STATUS_CHOICES = [
        ('pending',     'Pending — Awaiting Provider'),
        ('accepted',    'Accepted by Provider'),
        ('declined',    'Declined by Provider'),
        ('in_progress', 'Service In Progress'),
        ('completed',   'Completed'),
        ('cancelled',   'Cancelled by Customer'),
    ]
    VEHICLE_CHOICES = [
        ('car',        'Car / Sedan'),
        ('suv',        'SUV / MUV'),
        ('motorcycle', 'Motorcycle'),
        ('truck',      'Truck / Commercial'),
        ('other',      'Other'),
    ]

    customer          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    provider          = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='incoming_service_requests')
    # Service details
    service_type_text = models.CharField(max_length=200, help_text="Freeform service type requested by customer")
    vehicle_type      = models.CharField(max_length=20, choices=VEHICLE_CHOICES, default='car')
    vehicle_make      = models.CharField(max_length=100, blank=True, help_text="e.g. Maruti, Honda")
    vehicle_model     = models.CharField(max_length=100, blank=True, help_text="e.g. Swift, City")
    vehicle_year      = models.CharField(max_length=4, blank=True)
    vehicle_reg_no    = models.CharField(max_length=20, blank=True, help_text="Registration / Number plate")
    notes             = models.TextField(blank=True)
    location_address  = models.TextField(blank=True)
    # Status
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    provider_note     = models.TextField(blank=True, help_text="Note from provider when accepting or declining")
    # Timestamps
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)
    accepted_at       = models.DateTimeField(null=True, blank=True)
    completed_at      = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Service Request'
        verbose_name_plural = 'Service Requests'
        ordering            = ['-created_at']

    def __str__(self):
        return f"SR#{self.pk} — {self.customer.email} → {self.provider.business_name} [{self.get_status_display()}]"


class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=500)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Push Subscription'
        verbose_name_plural = 'Push Subscriptions'
        unique_together = ('user', 'endpoint')

    def __str__(self):
        return f"PushSubscription for {self.user.username}"

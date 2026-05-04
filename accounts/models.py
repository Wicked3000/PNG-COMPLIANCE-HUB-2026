"""Accounts App — Business Profile & Auth Models"""

from django.db import models
from django.contrib.auth.models import User


PNG_PROVINCES = [
    ('NCD', 'National Capital District'),
    ('WNB', 'West New Britain'),
    ('ENB', 'East New Britain'),
    ('MRL', 'Manus'),
    ('NIP', 'New Ireland'),
    ('MBP', 'Milne Bay'),
    ('ORO', 'Oro (Northern)'),
    ('CHM', 'Chimbu (Simbu)'),
    ('EHP', 'Eastern Highlands'),
    ('WHP', 'Western Highlands'),
    ('JWK', 'Jiwaka'),
    ('HLA', 'Hela'),
    ('SHM', 'Southern Highlands'),
    ('EPW', 'Enga'),
    ('WPD', 'Western (Fly)'),
    ('GPL', 'Gulf'),
    ('CPM', 'Central'),
    ('SAN', 'Sandaun (West Sepik)'),
    ('ESP', 'East Sepik'),
    ('MPM', 'Morobe'),
    ('MDP', 'Madang'),
    ('BUK', 'Bougainville'),
]

INDUSTRY_TYPES = [
    ('RETAIL',      'Retail & Trade Store'),
    ('FOOD',        'Food & Beverage / Canteen'),
    ('TRANSPORT',   'Transport & Logistics'),
    ('AGRI',        'Agriculture & Farming'),
    ('CONSTRUCT',   'Construction & Building'),
    ('HEALTH',      'Health & Medical'),
    ('EDUCATION',   'Education & Training'),
    ('PROFESSIONAL','Professional Services'),
    ('TOURISM',     'Tourism & Hospitality'),
    ('TECH',        'Technology & ICT'),
    ('FISHING',     'Fishing & Marine'),
    ('MINING',      'Mining & Extraction'),
    ('OTHER',       'Other'),
]

GST_FILING_FREQ = [
    ('MONTHLY',   'Monthly (turnover > K250,000)'),
    ('QUARTERLY', 'Quarterly'),
]


USER_ROLES = [
    ('OWNER',      'Business Owner'),
    ('ACCOUNTANT', 'External Accountant'),
    ('STAFF',      'Compliance Staff'),
]

NOTIFICATION_PREFS = [
    ('SMS',   'SMS (Mobile)'),
    ('EMAIL', 'Email'),
    ('BOTH',  'Both SMS & Email'),
    ('NONE',  'No Notifications'),
]


class BusinessProfile(models.Model):
    """Core business entity linked to a Django user account."""

    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business')
    business_name   = models.CharField(max_length=200)
    tin             = models.CharField(max_length=20, unique=True, verbose_name='IRC TIN', help_text='IRC Tax Identification Number')
    province        = models.CharField(max_length=10, choices=PNG_PROVINCES, default='NCD')
    industry        = models.CharField(max_length=20, choices=INDUSTRY_TYPES, default='RETAIL')
    phone           = models.CharField(max_length=20, blank=True)
    address         = models.TextField(blank=True)

    # Tax Registration
    gst_registered          = models.BooleanField(default=False, verbose_name='GST Registered?')
    gst_registration_number = models.CharField(max_length=30, blank=True)
    gst_filing_frequency    = models.CharField(max_length=10, choices=GST_FILING_FREQ, default='QUARTERLY')
    sbt_eligible            = models.BooleanField(default=True,  verbose_name='SBT Eligible?')
    annual_turnover_estimate= models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Phase 3: Enterprise Roles & Alerts
    role            = models.CharField(max_length=20, choices=USER_ROLES, default='OWNER')
    notify_method   = models.CharField(max_length=10, choices=NOTIFICATION_PREFS, default='BOTH')
    notify_days_before = models.IntegerField(default=3, help_text='Days before deadline to alert')

    # Metadata
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Business Profile'
        verbose_name_plural = 'Business Profiles'
        ordering            = ['business_name']

    def __str__(self):
        return f'{self.business_name} (TIN: {self.tin})'

    @property
    def owner_name(self):
        return self.user.get_full_name() or self.user.username


class UserCredential(models.Model):
    """Stores WebAuthn public keys for biometric authentication."""
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credentials')
    credential_id   = models.CharField(max_length=255, unique=True)
    public_key      = models.TextField()
    sign_count      = models.IntegerField(default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    device_name     = models.CharField(max_length=100, blank=True, default='Biometric Device')

    def __str__(self):
        return f'{self.user.username} - {self.device_name}'

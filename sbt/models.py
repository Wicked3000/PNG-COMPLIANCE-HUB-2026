"""SBT App — Small Business Tax Models"""

from django.db import models
from accounts.models import BusinessProfile


class SBTDeclaration(models.Model):
    """Annual Small Business Tax declaration filed with IRC."""

    STATUS_CHOICES = [
        ('DRAFT',     'Draft'),
        ('SUBMITTED', 'Submitted to IRC'),
        ('PAID',      'Payment Confirmed'),
        ('EXEMPT',    'Exempt / Threshold Exceeded'),
        ('OVERDUE',   'Overdue'),
    ]

    SBT_TYPE_CHOICES = [
        ('FLAT',    'Flat Fee (K400) — Turnover < K50,000'),
        ('PERCENT', '2% of Turnover — Turnover K50k–K250k'),
        ('EXEMPT',  'Not Eligible — Turnover > K250,000'),
    ]

    business          = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='sbt_declarations')
    tax_year          = models.PositiveIntegerField(default=2026)
    annual_turnover   = models.DecimalField(max_digits=14, decimal_places=2)
    sbt_type          = models.CharField(max_length=10, choices=SBT_TYPE_CHOICES)
    sbt_liability     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    submitted_at      = models.DateTimeField(null=True, blank=True)
    payment_ref       = models.CharField(max_length=50, blank=True)
    irc_reference     = models.CharField(max_length=50, blank=True)
    notes             = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'SBT Declaration'
        verbose_name_plural = 'SBT Declarations'
        ordering            = ['-tax_year']
        unique_together     = [['business', 'tax_year']]

    def __str__(self):
        return f'SBT {self.tax_year} | {self.business.business_name} | K{self.sbt_liability:,.2f}'

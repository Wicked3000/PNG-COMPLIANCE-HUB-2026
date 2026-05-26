"""GST App - Daily Ledger & GST Return Models"""

from django.db import models
from accounts.models import BusinessProfile


class DailyLedger(models.Model):
    """Records daily sales and purchases for GST calculation."""

    ENTRY_TYPE = [
        ('SALE',     'Sale / Revenue'),
        ('PURCHASE', 'Purchase / Expense'),
    ]

    business         = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='ledger_entries')
    date             = models.DateField()
    description      = models.CharField(max_length=200)
    entry_type       = models.CharField(max_length=10, choices=ENTRY_TYPE, default='SALE')

    # Amounts (GST-exclusive)
    amount_excl_gst  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    gst_amount       = models.DecimalField(max_digits=14, decimal_places=2, default=0, editable=False)
    amount_incl_gst  = models.DecimalField(max_digits=14, decimal_places=2, default=0, editable=False)

    receipt_ref      = models.CharField(max_length=50, blank=True, verbose_name='Receipt / Invoice Ref')
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Daily Ledger Entry'
        verbose_name_plural = 'Daily Ledger Entries'
        ordering            = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        """Auto-calculate GST amounts on save."""
        from decimal import Decimal
        gst_rate = Decimal('0.10')
        self.amount_excl_gst = Decimal(str(self.amount_excl_gst))
        self.gst_amount      = (self.amount_excl_gst * gst_rate).quantize(Decimal('0.01'))
        self.amount_incl_gst = self.amount_excl_gst + self.gst_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.date} | {self.entry_type} | K{self.amount_excl_gst:,.2f}'


class GSTReturn(models.Model):
    """Periodic GST return filing record."""

    STATUS_CHOICES = [
        ('DRAFT',     'Draft'),
        ('SUBMITTED', 'Submitted to IRC'),
        ('PAID',      'Payment Confirmed'),
        ('OVERDUE',   'Overdue'),
    ]

    business          = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='gst_returns')
    period_start      = models.DateField()
    period_end        = models.DateField()

    total_sales       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_purchases   = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    output_gst        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    input_gst         = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_gst           = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    status            = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT')
    submitted_at      = models.DateTimeField(null=True, blank=True)
    irc_reference     = models.CharField(max_length=50, blank=True, verbose_name='IRC Reference Number')
    notes             = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'GST Return'
        verbose_name_plural = 'GST Returns'
        ordering            = ['-period_end']

    # ── Property aliases for template compatibility ──────────────────
    # Templates reference these names; actual DB fields use shorter names.

    @property
    def total_sales_excl(self):
        """Alias for total_sales (GST-exclusive sales total)."""
        return self.total_sales

    @property
    def total_purchases_excl(self):
        """Alias for total_purchases (GST-exclusive purchases total)."""
        return self.total_purchases

    @property
    def total_output_gst(self):
        """Alias for output_gst."""
        return self.output_gst

    @property
    def total_input_gst(self):
        """Alias for input_gst."""
        return self.input_gst

    @property
    def net_gst_payable(self):
        """Alias for net_gst (absolute value of net GST owed or refundable)."""
        return abs(self.net_gst)

    @property
    def refund_due(self):
        """True when input credits exceed output GST (net_gst is negative)."""
        return self.net_gst < 0

    def __str__(self):
        return f'GST Return {self.period_start} – {self.period_end} | {self.status}'

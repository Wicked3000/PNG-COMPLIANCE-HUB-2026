"""SWT App - Employee & Payroll Models"""

from django.db import models
from accounts.models import BusinessProfile


class Employee(models.Model):
    """Employee record for SWT payroll calculation."""

    PAYMENT_FREQ = [
        ('WEEKLY',      'Weekly'),
        ('FORTNIGHTLY', 'Fortnightly'),
        ('MONTHLY',     'Monthly'),
    ]

    business        = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='employees')
    full_name       = models.CharField(max_length=150)
    tin             = models.CharField(max_length=20, blank=True, verbose_name='Employee TIN')
    position        = models.CharField(max_length=100, blank=True)
    is_resident     = models.BooleanField(default=True, verbose_name='PNG Resident?')
    payment_frequency = models.CharField(max_length=15, choices=PAYMENT_FREQ, default='FORTNIGHTLY')
    annual_salary   = models.DecimalField(max_digits=12, decimal_places=2)
    is_active       = models.BooleanField(default=True)
    hired_date      = models.DateField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Employee'
        verbose_name_plural = 'Employees'
        ordering            = ['full_name']

    @property
    def employee_id(self):
        """Auto-generated employee ID for display in payslips."""
        return f'EMP-{self.pk:04d}'

    def __str__(self):
        return f'{self.full_name} - K{self.annual_salary:,.2f}/yr'


class PayrollEntry(models.Model):
    """Individual payroll run record with SWT withheld."""

    employee        = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_entries')
    pay_period_start= models.DateField()
    pay_period_end  = models.DateField()
    gross_salary    = models.DecimalField(max_digits=12, decimal_places=2)
    swt_withheld    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_remitted     = models.BooleanField(default=False, verbose_name='SWT Remitted to IRC?')
    remittance_ref  = models.CharField(max_length=50, blank=True)
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Payroll Entry'
        verbose_name_plural = 'Payroll Entries'
        ordering            = ['-pay_period_end']

    # ── Property aliases for template compatibility ──────────────────

    @property
    def pay_date(self):
        """Alias: templates use pay_date, model stores pay_period_end."""
        return self.pay_period_end

    @property
    def period_start(self):
        """Alias: templates use period_start, model stores pay_period_start."""
        return self.pay_period_start

    @property
    def gross_pay(self):
        """Alias: templates use gross_pay, model stores gross_salary."""
        return self.gross_salary

    @property
    def tax_withheld(self):
        """Alias: templates use tax_withheld, model stores swt_withheld."""
        return self.swt_withheld

    def __str__(self):
        return f'{self.employee.full_name} | {self.pay_period_end} | SWT: K{self.swt_withheld:,.2f}'


class SWTReturn(models.Model):
    """Monthly SWT remittance return filed with IRC."""

    STATUS_CHOICES = [
        ('DRAFT',     'Draft'),
        ('SUBMITTED', 'Submitted to IRC'),
        ('PAID',      'Payment Confirmed'),
        ('OVERDUE',   'Overdue'),
    ]

    business        = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='swt_returns')
    month           = models.DateField(verbose_name='Return Month (1st of month)')
    total_gross     = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_swt       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    employee_count  = models.PositiveIntegerField(default=0)
    status          = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT')
    submitted_at    = models.DateTimeField(null=True, blank=True)
    irc_reference   = models.CharField(max_length=50, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'SWT Return'
        verbose_name_plural = 'SWT Returns'
        ordering            = ['-month']

    def __str__(self):
        return f'SWT Return {self.month.strftime("%B %Y")} | K{self.total_swt:,.2f}'

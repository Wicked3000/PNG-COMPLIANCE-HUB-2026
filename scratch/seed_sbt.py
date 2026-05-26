"""Seed SBT test data."""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compliance_hub.settings')
django.setup()

from django.contrib.auth.models import User
from sbt.models import SBTDeclaration
from core.tax_engine import TaxCalculator
from datetime import date
from decimal import Decimal

u = User.objects.get(username='admin')
bp = u.business

# SBT Declaration for 2026 (Draft)
annual_turnover = Decimal('185000.00')
result = TaxCalculator.calculate_sbt(annual_turnover)

sbt, created = SBTDeclaration.objects.get_or_create(
    business=bp,
    tax_year=2026,
    defaults={
        'annual_turnover': annual_turnover,
        'sbt_type': 'PERCENT',
        'sbt_liability': result['sbt_liability'],
        'status': 'DRAFT',
    }
)
print(f"SBT 2026: Turnover=K{annual_turnover} | Liability=K{result['sbt_liability']} (created={created})")

# SBT Declaration for 2025 (Paid - historical)
sbt25, created = SBTDeclaration.objects.get_or_create(
    business=bp,
    tax_year=2025,
    defaults={
        'annual_turnover': Decimal('142000.00'),
        'sbt_type': 'PERCENT',
        'sbt_liability': Decimal('2840.00'),
        'status': 'PAID',
        'payment_ref': 'BSP-REF-20250331-001',
    }
)
print(f"SBT 2025: K142,000 turnover | K2,840 liability (created={created})")
print("--- SBT data done ---")
print()
print("=== ALL TEST DATA CREATED SUCCESSFULLY ===")
print()
print("Login: admin / admin123")
print()
print("Test these URLs now:")
print("  Reports Hub:      http://127.0.0.1:8000/reports/")
print("  GST Returns:      http://127.0.0.1:8000/gst/returns/")
print("  SWT Dashboard:    http://127.0.0.1:8000/swt/")
print("  SBT Dashboard:    http://127.0.0.1:8000/sbt/")

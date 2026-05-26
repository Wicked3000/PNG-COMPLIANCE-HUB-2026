"""SBT App - Views"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from core.tax_engine import TaxCalculator
from .models import SBTDeclaration


@login_required
def sbt_dashboard(request):
    business = request.user.business
    sbt_data = TaxCalculator.calculate_sbt(business.annual_turnover_estimate)
    declarations = SBTDeclaration.objects.filter(business=business)
    return render(request, 'sbt/dashboard.html', {
        'sbt_data': sbt_data, 'declarations': declarations, 'business': business
    })


@login_required
def calculator(request):
    result = None
    if request.method == 'POST':
        turnover = Decimal(request.POST.get('turnover', '0') or '0')
        result = TaxCalculator.calculate_sbt(turnover)
    return render(request, 'sbt/calculator.html', {'result': result})


@login_required
def declare(request):
    business = request.user.business
    if request.method == 'POST':
        turnover = Decimal(request.POST.get('annual_turnover', '0') or '0')
        sbt = TaxCalculator.calculate_sbt(turnover)
        from django.utils import timezone
        from core.models import SystemSettings
        
        active_year = SystemSettings.load().active_tax_year
        SBTDeclaration.objects.update_or_create(
            business=business, tax_year=active_year,
            defaults={
                'annual_turnover': turnover,
                'sbt_type': 'FLAT' if sbt['sbt_type'] == 'Flat Fee' else ('PERCENT' if sbt.get('rate_display') else 'EXEMPT'),
                'sbt_liability': sbt['sbt_liability'],
                'status': 'DRAFT',
            }
        )
        return redirect('sbt:dashboard')
    return render(request, 'sbt/declare.html', {'business': business})

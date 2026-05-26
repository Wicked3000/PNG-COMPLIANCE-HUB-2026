"""GST App - Views"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from core.tax_engine import TaxCalculator
from .models import DailyLedger, GSTReturn


@login_required
def gst_dashboard(request):
    business = request.user.business
    today = timezone.localdate()
    entries = DailyLedger.objects.filter(business=business, date__month=today.month, date__year=today.year)
    sales = entries.filter(entry_type='SALE').aggregate(t=Sum('amount_excl_gst'))['t'] or 0
    purchases = entries.filter(entry_type='PURCHASE').aggregate(t=Sum('amount_excl_gst'))['t'] or 0
    gst_data = TaxCalculator.calculate_gst(Decimal(str(sales)), Decimal(str(purchases)))
    return render(request, 'gst/dashboard.html', {
        'gst_data': gst_data, 'entries': entries[:10], 'business': business
    })


@login_required
def ledger(request):
    business = request.user.business
    entries = DailyLedger.objects.filter(business=business)
    return render(request, 'gst/ledger.html', {'entries': entries, 'business': business})


@login_required
def add_entry(request):
    business = request.user.business
    if request.method == 'POST':
        DailyLedger.objects.create(
            business=business,
            date=request.POST.get('date'),
            description=request.POST.get('description'),
            entry_type=request.POST.get('entry_type', 'SALE'),
            amount_excl_gst=request.POST.get('amount', 0),
            receipt_ref=request.POST.get('receipt_ref', ''),
            notes=request.POST.get('notes', ''),
        )
        if request.htmx:
            return render(request, 'gst/partials/entry_row.html')
        return redirect('gst:ledger')
    return render(request, 'gst/add_entry.html', {'business': business})


@login_required
def returns_list(request):
    business = request.user.business
    returns = GSTReturn.objects.filter(business=business)
    return render(request, 'gst/returns.html', {'returns': returns, 'business': business})


@login_required
def calculator(request):
    result = None
    if request.method == 'POST':
        sales = Decimal(request.POST.get('sales', '0') or '0')
        purchases = Decimal(request.POST.get('purchases', '0') or '0')
        result = TaxCalculator.calculate_gst(sales, purchases)
    return render(request, 'gst/calculator.html', {'result': result})

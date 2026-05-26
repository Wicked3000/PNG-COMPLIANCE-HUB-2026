"""Dashboard App - Views"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from core.tax_engine import TaxCalculator


from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def landing_page(request):
    """Public SaaS Landing Page."""
    return render(request, 'landing.html')

@login_required
@ensure_csrf_cookie
def dashboard(request):
    """Main compliance dashboard view."""
    try:
        business = request.user.business
    except Exception:
        return redirect('accounts:setup')

    today = timezone.localdate()

    # ── Pull aggregated data ──────────────────────────────────────────────────
    from gst.models import DailyLedger, GSTReturn
    from swt.models import PayrollEntry, SWTReturn
    from sbt.models import SBTDeclaration

    # Current month ledger totals
    month_sales     = DailyLedger.objects.filter(
        business=business, date__month=today.month,
        date__year=today.year, entry_type='SALE'
    ).aggregate(total=Sum('amount_excl_gst'))['total'] or Decimal('0')

    month_purchases = DailyLedger.objects.filter(
        business=business, date__month=today.month,
        date__year=today.year, entry_type='PURCHASE'
    ).aggregate(total=Sum('amount_excl_gst'))['total'] or Decimal('0')

    gst_data   = TaxCalculator.calculate_gst(month_sales, month_purchases)
    sbt_data   = TaxCalculator.calculate_sbt(business.annual_turnover_estimate)

    # Recent SWT
    recent_swt = SWTReturn.objects.filter(business=business).first()
    swt_owing  = recent_swt.total_swt if recent_swt else Decimal('0')

    # Next filing date (21st of next month)
    if today.month == 12:
        next_filing = today.replace(year=today.year + 1, month=1, day=21)
    else:
        next_filing = today.replace(month=today.month + 1, day=21)

    # Chart data - last 6 months revenue vs tax
    chart_labels   = []
    chart_revenue  = []
    chart_tax      = []
    for i in range(5, -1, -1):
        m = (today.month - i - 1) % 12 + 1
        y = today.year if today.month - i > 0 else today.year - 1
        sales_m = DailyLedger.objects.filter(
            business=business, date__month=m, date__year=y, entry_type='SALE'
        ).aggregate(total=Sum('amount_excl_gst'))['total'] or 0
        gst_m   = float(sales_m) * 0.10
        chart_labels.append(timezone.datetime(y, m, 1).strftime('%b %Y'))
        chart_revenue.append(float(sales_m))
        chart_tax.append(round(gst_m, 2))

    # Compliance score (simple heuristic)
    compliance_score = _compute_compliance_score(business)

    # Activity Feed Data
    recent_ledger = DailyLedger.objects.filter(business=business).order_by('-date', '-id')[:5]
    recent_payroll = PayrollEntry.objects.filter(employee__business=business).order_by('-id')[:5]
    
    # Combined filings (limit to 5)
    filings = []
    for r in GSTReturn.objects.filter(business=business).order_by('-period_end')[:3]:
        filings.append({'type': 'GST', 'label': f"GST {r.period_start.strftime('%b %Y')}", 'status': r.status, 'status_display': r.get_status_display(), 'date': r.period_end})
    for r in SWTReturn.objects.filter(business=business).order_by('-month')[:3]:
        filings.append({'type': 'SWT', 'label': f"SWT {r.month.strftime('%b %Y')}", 'status': r.status, 'status_display': r.get_status_display(), 'date': r.month})
    for r in SBTDeclaration.objects.filter(business=business).order_by('-tax_year')[:3]:
        filings.append({'type': 'SBT', 'label': f'SBT {r.tax_year}', 'status': r.status, 'status_display': r.get_status_display(), 'date': timezone.datetime(r.tax_year, 12, 31).date()})
    
    filings.sort(key=lambda x: x['date'], reverse=True)
    recent_filings = filings[:5]

    context = {
        'business':          business,
        'today':             today,
        'next_filing':       next_filing,
        'gst_data':          gst_data,
        'sbt_data':          sbt_data,
        'swt_owing':         swt_owing,
        'month_sales':       month_sales,
        'compliance_score':  compliance_score,
        'chart_labels':      chart_labels,
        'chart_revenue':     chart_revenue,
        'chart_tax':         chart_tax,
        'recent_ledger':     recent_ledger,
        'recent_payroll':    recent_payroll,
        'recent_filings':    recent_filings,
    }
    return render(request, 'dashboard/index.html', context)


def _compute_compliance_score(business) -> int:
    """Dynamic compliance score (0-100) based on profile and filing status."""
    score = 50
    # Profile Completion (40%)
    if business.tin:              score += 15
    if business.gst_registered:   score += 10
    if business.phone:             score +=  5
    if business.address:           score +=  5
    if business.annual_turnover_estimate > 0: score += 5
    
    # Filing Discipline (Penalty System)
    from gst.models import GSTReturn
    from swt.models import SWTReturn
    
    overdue_gst = GSTReturn.objects.filter(business=business, status='OVERDUE').count()
    overdue_swt = SWTReturn.objects.filter(business=business, status='OVERDUE').count()
    
    score -= (overdue_gst * 10)
    score -= (overdue_swt * 10)
    
    return max(0, min(score, 100))


# ── HTMX Partial: Quick Log Sale ─────────────────────────────────────────────

@login_required
def quick_log_sale(request):
    """HTMX endpoint - Quick Sale FAB modal submit."""
    from gst.forms import QuickSaleForm
    if request.method == 'POST':
        form = QuickSaleForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.business = request.user.business
            entry.entry_type = 'SALE'
            entry.save()
            return render(request, 'dashboard/partials/sale_success.html', {'entry': entry})
    else:
        form = QuickSaleForm()
    return render(request, 'dashboard/partials/quick_log_form.html', {'form': form})



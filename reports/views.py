"""Reports App — Views (WeasyPrint PDF generation)"""

import logging
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import timedelta

from gst.models import GSTReturn
from swt.models import SWTReturn
from sbt.models import SBTDeclaration

logger = logging.getLogger(__name__)

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception as e:
    logger.warning(f"WeasyPrint not available: {e}. Falling back to HTML print views.")
    WEASYPRINT_AVAILABLE = False


def _generate_pdf_response(template_name, context, filename):
    """Helper to generate PDF or fallback HTML."""
    html_string = render_to_string(template_name, context)
    
    # In this environment, we force HTML fallback for reliability
    if WEASYPRINT_AVAILABLE and not settings.DEBUG:
        try:
            pdf = HTML(string=html_string).write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            return response
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")

    # Fallback: Return HTML for browser printing
    return HttpResponse(html_string)


@login_required
def reports_home(request):
    business = request.user.business
    gst_returns = GSTReturn.objects.filter(business=business)
    swt_returns = SWTReturn.objects.filter(business=business)
    sbt_returns = SBTDeclaration.objects.filter(business=business)
    return render(request, 'reports/home.html', {
        'gst_returns': gst_returns, 'swt_returns': swt_returns,
        'sbt_returns': sbt_returns, 'business': business,
    })


@login_required
def gst_return_pdf(request, pk):
    res = get_object_or_404(GSTReturn, pk=pk, business=request.user.business)
    context = {
        'return': res,
        'due_date': res.period_start + timedelta(days=51),
    }
    return _generate_pdf_response('reports/pdf/gst_return_pdf.html', context, f"GSTS65A_{res.period_start.strftime('%Y%m')}")


@login_required
def swt_return_pdf(request, pk):
    res = get_object_or_404(SWTReturn, pk=pk, business=request.user.business)
    context = {
        'return': res,
        'due_date': res.month + timedelta(days=37),
        'employee_count': res.business.employees.filter(is_active=True).count(),
    }
    return _generate_pdf_response('reports/pdf/swt_return_pdf.html', context, f"SWT_Return_{res.month.strftime('%Y%m')}")


@login_required
def sbt_return_pdf(request, pk):
    res = get_object_or_404(SBTDeclaration, pk=pk, business=request.user.business)
    context = {
        'return': res,
    }
    return _generate_pdf_response('reports/pdf/sbt_return_pdf.html', context, f"SBT_Declaration_{res.tax_year}")

@login_required
def payment_voucher_pdf(request, tax_type, amount):
    """Generate a bank-ready IRC payment voucher."""
    business = request.user.business
    tax_codes = {
        'gst': {'code': '012', 'name': 'Goods and Services Tax'},
        'swt': {'code': '011', 'name': 'Salary & Wages Tax'},
        'sbt': {'code': '013', 'name': 'Small Business Tax'},
    }
    info = tax_codes.get(tax_type.lower(), {'code': '???', 'name': 'Unknown Tax'})
    
    context = {
        'business': business,
        'tax_type_name': info['name'],
        'tax_code': info['code'],
        'amount': float(amount),
        'period_name': 'Current Period 2026'
    }
    return _generate_pdf_response('reports/pdf/irc_payment_voucher.html', context, f"IRC_Payment_Voucher_{tax_type}")

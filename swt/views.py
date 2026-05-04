"""SWT App — Views"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from core.tax_engine import TaxCalculator
from .models import Employee, PayrollEntry, SWTReturn


@login_required
def swt_dashboard(request):
    business = request.user.business
    employees = Employee.objects.filter(business=business, is_active=True)
    recent_return = SWTReturn.objects.filter(business=business).first()
    return render(request, 'swt/dashboard.html', {
        'employees': employees, 'recent_return': recent_return, 'business': business
    })


@login_required
def employees(request):
    business = request.user.business
    if request.method == 'POST':
        Employee.objects.create(
            business=business,
            full_name=request.POST.get('full_name'),
            tin=request.POST.get('tin', ''),
            position=request.POST.get('position', ''),
            is_resident=request.POST.get('is_resident') == 'on',
            payment_frequency=request.POST.get('payment_frequency', 'FORTNIGHTLY'),
            annual_salary=request.POST.get('annual_salary', 0),
        )
        return redirect('swt:employees')
    emps = Employee.objects.filter(business=business)
    return render(request, 'swt/employees.html', {'employees': emps, 'business': business})


@login_required
def payroll(request):
    business = request.user.business
    entries = PayrollEntry.objects.filter(employee__business=business)
    return render(request, 'swt/payroll.html', {'entries': entries, 'business': business})


@login_required
def calculator(request):
    result = None
    if request.method == 'POST':
        salary = Decimal(request.POST.get('salary', '0') or '0')
        is_resident = request.POST.get('is_resident', 'true') == 'true'
        result = TaxCalculator.calculate_swt(salary, is_resident)
    return render(request, 'swt/calculator.html', {'result': result})


@login_required
def returns_list(request):
    business = request.user.business
    returns = SWTReturn.objects.filter(business=business)
    return render(request, 'swt/returns.html', {'returns': returns, 'business': business})

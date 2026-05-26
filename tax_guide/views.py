from django.shortcuts import render
from django.http import Http404

TAX_GUIDES = {
    'gst-basics': {
        'title': 'GST Basics for PNG MSMEs',
        'content': 'Understanding Goods and Services Tax\n\nGST in Papua New Guinea is a 10% tax added to the price of most goods and services. If your annual turnover exceeds K250,000, you are legally required to register with the IRC.',
        'icon': 'bi-receipt'
    },
    'swt-payroll': {
        'title': 'Managing SWT & Payroll',
        'content': 'Salary & Wages Tax (SWT)\n\nEmployers are responsible for withholding tax from employee wages and remitting it to the IRC by the 7th day of the following month.',
        'icon': 'bi-people'
    },
    'sbt-rules': {
        'title': 'Small Business Tax (SBT) Rules',
        'content': 'Is your business SBT eligible?\n\nSBT is a simplified tax for businesses with a turnover between K50,000 and K250,000. The rate is 2% of turnover plus a small annual fee.',
        'icon': 'bi-shop'
    }
}

def guide_list(request):
    return render(request, 'tax_guide/index.html', {'guides': TAX_GUIDES})

def guide_detail(request, slug):
    guide = TAX_GUIDES.get(slug)
    if not guide: raise Http404()
    return render(request, 'tax_guide/detail.html', {'guide': guide})

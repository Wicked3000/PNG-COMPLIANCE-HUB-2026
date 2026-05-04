"""GST Forms — Quick Sale HTMX Form"""
from django import forms
from .models import DailyLedger
from django.utils import timezone


class QuickSaleForm(forms.ModelForm):
    class Meta:
        model   = DailyLedger
        fields  = ['date', 'description', 'amount_excl_gst', 'receipt_ref']
        widgets = {
            'date':           forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Retail sales — canteen'}),
            'amount_excl_gst':forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'receipt_ref':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Receipt #'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial      = timezone.localdate()
        self.fields['receipt_ref'].required = False

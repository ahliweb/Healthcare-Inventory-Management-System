from django import forms
from django.forms import inlineformset_factory

from .models import Expired, ExpiredItem


class ExpiredForm(forms.ModelForm):
    class Meta:
        model = Expired
        fields = ['document_number', 'report_date', 'notes']
        widgets = {
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'report_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ExpiredItemForm(forms.ModelForm):
    class Meta:
        model = ExpiredItem
        fields = ['item', 'stock', 'quantity', 'notes']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'stock': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0.01', 'step': '0.01'}),
            'notes': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        stock = cleaned_data.get('stock')
        quantity = cleaned_data.get('quantity')

        if stock and item and stock.item_id != item.id:
            self.add_error('stock', 'Batch stok harus sesuai dengan barang yang dipilih.')

        if quantity is not None and quantity <= 0:
            self.add_error('quantity', 'Jumlah harus lebih dari 0.')

        return cleaned_data


ExpiredItemFormSet = inlineformset_factory(
    Expired,
    ExpiredItem,
    form=ExpiredItemForm,
    extra=3,
    can_delete=True,
)

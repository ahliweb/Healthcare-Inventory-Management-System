from django import forms
from django.forms import inlineformset_factory

from .models import Recall, RecallItem


class RecallForm(forms.ModelForm):
    class Meta:
        model = Recall
        fields = ['document_number', 'recall_date', 'supplier', 'notes']
        widgets = {
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'recall_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RecallItemForm(forms.ModelForm):
    class Meta:
        model = RecallItem
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


RecallItemFormSet = inlineformset_factory(
    Recall,
    RecallItem,
    form=RecallItemForm,
    extra=3,
    can_delete=True,
)

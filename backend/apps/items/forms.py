from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'nama_barang', 'satuan', 'kategori',
            'is_program_item', 'program', 'minimum_stock', 'description',
        ]
        widgets = {
            'nama_barang': forms.TextInput(attrs={'class': 'form-control'}),
            'satuan': forms.Select(attrs={'class': 'form-select'}),
            'kategori': forms.Select(attrs={'class': 'form-select'}),
            'is_program_item': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'program': forms.Select(attrs={'class': 'form-select'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['program'].required = False

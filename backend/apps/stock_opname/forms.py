from django import forms
from .models import StockOpname


class StockOpnameForm(forms.ModelForm):
    class Meta:
        model = StockOpname
        fields = ['period_type', 'period_start', 'period_end', 'notes']
        widgets = {
            'period_type': forms.Select(attrs={'class': 'form-select'}),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'period_type': 'Tipe Periode',
            'period_start': 'Tanggal Mulai',
            'period_end': 'Tanggal Selesai',
            'notes': 'Catatan',
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('period_start')
        end = cleaned_data.get('period_end')
        if start and end and start > end:
            raise forms.ValidationError('Tanggal mulai tidak boleh lebih besar dari tanggal selesai.')
        return cleaned_data

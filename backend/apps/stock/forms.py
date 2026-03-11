from django import forms

from apps.items.models import Location

from .models import StockTransfer


class StockTransferForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ["transfer_date", "source_location", "destination_location", "notes"]
        widgets = {
            "transfer_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "source_location": forms.Select(attrs={"class": "form-select"}),
            "destination_location": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_locations = Location.objects.filter(is_active=True).order_by("code")
        self.fields["source_location"].queryset = active_locations
        self.fields["destination_location"].queryset = active_locations

    def clean(self):
        cleaned = super().clean()
        source = cleaned.get("source_location")
        destination = cleaned.get("destination_location")
        if source and destination and source == destination:
            self.add_error(
                "destination_location",
                "Lokasi tujuan harus berbeda dari lokasi asal.",
            )
        return cleaned

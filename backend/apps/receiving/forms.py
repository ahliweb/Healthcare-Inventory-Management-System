from django import forms
from django.forms import inlineformset_factory
from .models import Receiving, ReceivingItem, ReceivingOrderItem


class ReceivingForm(forms.ModelForm):
    class Meta:
        model = Receiving
        fields = [
            "document_number",
            "receiving_type",
            "receiving_date",
            "supplier",
            "sumber_dana",
            "notes",
        ]
        widgets = {
            "document_number": forms.TextInput(attrs={"class": "form-control"}),
            "receiving_type": forms.Select(attrs={"class": "form-select"}),
            "receiving_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "sumber_dana": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class PlannedReceivingForm(forms.ModelForm):
    class Meta:
        model = Receiving
        fields = [
            "document_number",
            "receiving_type",
            "receiving_date",
            "supplier",
            "sumber_dana",
            "notes",
        ]
        widgets = {
            "document_number": forms.TextInput(attrs={"class": "form-control"}),
            "receiving_type": forms.Select(attrs={"class": "form-select"}),
            "receiving_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "sumber_dana": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class ReceivingItemForm(forms.ModelForm):
    class Meta:
        model = ReceivingItem
        fields = ["item", "quantity", "batch_lot", "expiry_date", "unit_price"]
        widgets = {
            "item": forms.Select(
                attrs={"class": "form-select form-select-sm js-typeahead-select"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control form-control-sm", "min": "1"}
            ),
            "batch_lot": forms.TextInput(
                attrs={"class": "form-control form-control-sm"}
            ),
            "expiry_date": forms.DateInput(
                attrs={"class": "form-control form-control-sm", "type": "date"}
            ),
            "unit_price": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-sm",
                    "min": "0",
                    "step": "0.01",
                }
            ),
        }


ReceivingItemFormSet = inlineformset_factory(
    Receiving,
    ReceivingItem,
    form=ReceivingItemForm,
    extra=3,
    can_delete=True,
)


class ReceivingOrderItemForm(forms.ModelForm):
    class Meta:
        model = ReceivingOrderItem
        fields = ["item", "planned_quantity", "unit_price", "notes"]
        widgets = {
            "item": forms.Select(
                attrs={"class": "form-select form-select-sm js-typeahead-select"}
            ),
            "planned_quantity": forms.NumberInput(
                attrs={"class": "form-control form-control-sm", "min": "1"}
            ),
            "unit_price": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-sm",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "notes": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
        }


ReceivingOrderItemFormSet = inlineformset_factory(
    Receiving,
    ReceivingOrderItem,
    form=ReceivingOrderItemForm,
    extra=3,
    can_delete=True,
)


class ReceivingReceiptItemForm(forms.ModelForm):
    order_item = forms.ModelChoiceField(
        queryset=ReceivingOrderItem.objects.none(),
        widget=forms.Select(
            attrs={"class": "form-select form-select-sm js-typeahead-select"}
        ),
        required=True,
    )

    class Meta:
        model = ReceivingItem
        fields = [
            "order_item",
            "quantity",
            "batch_lot",
            "expiry_date",
            "unit_price",
            "location",
        ]
        widgets = {
            "quantity": forms.NumberInput(
                attrs={"class": "form-control form-control-sm", "min": "1"}
            ),
            "batch_lot": forms.TextInput(
                attrs={"class": "form-control form-control-sm"}
            ),
            "expiry_date": forms.DateInput(
                attrs={"class": "form-control form-control-sm", "type": "date"}
            ),
            "unit_price": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-sm",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "location": forms.Select(attrs={"class": "form-select form-select-sm"}),
        }

    def __init__(self, *args, **kwargs):
        receiving = kwargs.pop("receiving", None)
        super().__init__(*args, **kwargs)
        if receiving is not None:
            self.fields["order_item"].queryset = ReceivingOrderItem.objects.filter(
                receiving=receiving,
                is_cancelled=False,
            )
        self.fields["order_item"].label_from_instance = lambda obj: (
            f"{obj.item} (Sisa: {obj.remaining_quantity})"
        )

    def clean(self):
        cleaned = super().clean()
        order_item = cleaned.get("order_item")
        quantity = cleaned.get("quantity")
        if not order_item or quantity is None:
            return cleaned
        if order_item.is_cancelled:
            self.add_error("order_item", "Item pesanan ini sudah dibatalkan.")
        if order_item.remaining_quantity < quantity:
            self.add_error("quantity", "Jumlah melebihi sisa pesanan.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.order_item_id:
            instance.item = instance.order_item.item
        if commit:
            instance.save()
        return instance


ReceivingReceiptItemFormSet = inlineformset_factory(
    Receiving,
    ReceivingItem,
    form=ReceivingReceiptItemForm,
    extra=3,
    can_delete=True,
)


class ReceivingCloseForm(forms.Form):
    closed_reason = forms.CharField(
        label="Alasan Penutupan",
        required=True,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


class ReceivingOrderCloseItemForm(forms.ModelForm):
    class Meta:
        model = ReceivingOrderItem
        fields = ["is_cancelled", "cancel_reason"]
        widgets = {
            "is_cancelled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "cancel_reason": forms.TextInput(
                attrs={"class": "form-control form-control-sm"}
            ),
        }


ReceivingOrderCloseItemFormSet = inlineformset_factory(
    Receiving,
    ReceivingOrderItem,
    form=ReceivingOrderCloseItemForm,
    extra=0,
    can_delete=False,
)

from django import forms
from django.core.exceptions import ValidationError
from datetime import date

class PropertySearchForm(forms.Form):
    location = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter city or country',
            'data-location-search': True
        })
    )
    check_in = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        })
    )
    check_out = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        })
    )
    guests = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '20'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            if check_in < date.today():
                raise ValidationError("Check-in date cannot be in the past")
            if check_out <= check_in:
                raise ValidationError("Check-out date must be after check-in date")

        return cleaned_data


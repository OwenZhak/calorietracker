"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import FoodItemLog

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses bootstrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class FoodItemLogForm(forms.ModelForm):
    class Meta:
        model = FoodItemLog
        fields = ['food_item', 'quantity_in_grams']
        widgets = {
            'food_item': forms.Select(attrs={'class': 'form-control'}),
            'quantity_in_grams': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity in grams'}),
        }

    def clean_quantity_in_grams(self):
        quantity = self.cleaned_data.get('quantity_in_grams')
        if quantity <= 0:
            raise forms.ValidationError("Quantity in grams must be greater than 0.")
        return quantity

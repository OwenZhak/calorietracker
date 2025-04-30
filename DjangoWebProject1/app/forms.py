"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from dal import autocomplete
from .models import FoodItemLog, FoodItem, Profile, PendingFoodItem  

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
            'food_item': autocomplete.ModelSelect2(
                url='fooditem-autocomplete',  # This URL must be configured in your urls.py
                attrs={
                    'data-placeholder': 'Select a Food Item...',
                    'class': 'form-control'
                }
            ),
            'quantity_in_grams': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Quantity in grams'
                }
            ),
        }

    def clean_quantity_in_grams(self):
        quantity = self.cleaned_data.get('quantity_in_grams')
        if quantity <= 0:
            raise forms.ValidationError("Quantity in grams must be greater than 0.")
        return quantity

class EditFoodItemLogForm(forms.ModelForm):
    class Meta:
        model = FoodItemLog
        fields = ['food_item', 'quantity_in_grams']
        widgets = {
            'food_item': autocomplete.ModelSelect2(
                url='fooditem-autocomplete',  # This URL must be configured in your urls.py
                attrs={
                    'data-placeholder': 'Select a Food Item...',
                    'data-minimum-input-length': 2,
                    'class': 'form-control'
                }
            ),
            'quantity_in_grams': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity in grams'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['height', 'weight', 'age', 'gender', 'activity_level', 'weight_goal']
        widgets = {
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'activity_level': forms.Select(attrs={'class': 'form-control'}),
            'weight_goal': forms.Select(attrs={'class': 'form-control'}),
        }
        
        
class PendingFoodItemForm(forms.ModelForm):
    class Meta:
        model = PendingFoodItem
        fields = ['name', 'manufacturer', 'category', 'calories_per_100g', 
                 'proteins_per_100g', 'carbohydrates_per_100g', 'fats_per_100g']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'calories_per_100g': forms.NumberInput(attrs={'class': 'form-control'}),
            'proteins_per_100g': forms.NumberInput(attrs={'class': 'form-control'}),
            'carbohydrates_per_100g': forms.NumberInput(attrs={'class': 'form-control'}),
            'fats_per_100g': forms.NumberInput(attrs={'class': 'form-control'}),
        }
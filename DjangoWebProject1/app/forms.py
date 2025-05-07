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
                    'data-placeholder': 'Виберіть продукт...',
                    'class': 'form-control'
                }
            ),
            'quantity_in_grams': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Кількість в грамах',
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
                    'data-placeholder': 'Виберіть продукт...',
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
        labels = {
            'name': 'Назва продукту',
            'manufacturer': 'Виробник',
            'category': 'Категорія',
            'calories_per_100g': 'Калорії на 100г',
            'proteins_per_100g': 'Білки на 100г',
            'carbohydrates_per_100g': 'Вуглеводи на 100г',
            'fats_per_100g': 'Жири на 100г',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть назву продукту'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть назву виробника'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'calories_per_100g': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть кількість калорій на 100г',
                'min': '0'
            }),
            'proteins_per_100g': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть кількість білків на 100г',
                'min': '0'
            }),
            'carbohydrates_per_100g': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть кількість вуглеводів на 100г',
                'min': '0'
            }),
            'fats_per_100g': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть кількість жирів на 100г',
                'min': '0'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.replace(' ', '').isalpha():
            raise forms.ValidationError("Назва продукту повинна містити лише літери та пробіли")
        return name

    def clean_manufacturer(self):
        manufacturer = self.cleaned_data.get('manufacturer')
        if not manufacturer.replace(' ', '').isalpha():
            raise forms.ValidationError("Назва виробника повинна містити лише літери та пробіли")
        return manufacturer

    def clean_calories_per_100g(self):
        calories = self.cleaned_data.get('calories_per_100g')
        if calories <= 0:
            raise forms.ValidationError("Калорії повинні бути більше 0")
        return calories

    def clean_proteins_per_100g(self):
        proteins = self.cleaned_data.get('proteins_per_100g')
        if proteins < 0:
            raise forms.ValidationError("Кількість білків не може бути від'ємною")
        return proteins

    def clean_carbohydrates_per_100g(self):
        carbs = self.cleaned_data.get('carbohydrates_per_100g')
        if carbs < 0:
            raise forms.ValidationError("Кількість вуглеводів не може бути від'ємною")
        return carbs

    def clean_fats_per_100g(self):
        fats = self.cleaned_data.get('fats_per_100g')
        if fats < 0:
            raise forms.ValidationError("Кількість жирів не може бути від'ємною")
        return fats

    def clean(self):
        cleaned_data = super().clean()
        proteins = cleaned_data.get('proteins_per_100g', 0)
        carbs = cleaned_data.get('carbohydrates_per_100g', 0)
        fats = cleaned_data.get('fats_per_100g', 0)
        
        if proteins + carbs + fats > 100:
            raise forms.ValidationError(
                "Сума білків, вуглеводів та жирів не може перевищувати 100г"
            )
        return cleaned_data
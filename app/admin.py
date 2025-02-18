from django.contrib import admin
from .models import FoodItem, FoodItemLog

admin.site.register(FoodItem)
admin.site.register(FoodItemLog)
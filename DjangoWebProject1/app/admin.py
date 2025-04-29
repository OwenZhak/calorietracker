from django.contrib import admin
from .models import FoodItem, FoodItemLog, PendingFoodItem

admin.site.register(FoodItem)
admin.site.register(FoodItemLog)
admin.site.register(PendingFoodItem)
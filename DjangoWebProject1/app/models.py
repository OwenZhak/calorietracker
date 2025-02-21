from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    calories_per_100g = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.manufacturer})"

class FoodItemLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    date = models.DateField()
    quantity_in_grams = models.FloatField()

    @property
    def total_calories(self):
        return (self.quantity_in_grams / 100) * self.food_item.calories_per_100g
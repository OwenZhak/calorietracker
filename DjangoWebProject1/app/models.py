from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    calories_per_100g = models.FloatField()
    proteins_per_100g = models.FloatField(default=0)
    carbohydrates_per_100g = models.FloatField(default=0)
    fats_per_100g = models.FloatField(default=0)

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

    @property
    def total_proteins(self):
        return (self.quantity_in_grams / 100) * self.food_item.proteins_per_100g

    @property
    def total_carbohydrates(self):
        return (self.quantity_in_grams / 100) * self.food_item.carbohydrates_per_100g

    @property
    def total_fats(self):
        return (self.quantity_in_grams / 100) * self.food_item.fats_per_100g
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    age = models.IntegerField(default=25)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    @property
    def calculate_bmr(self):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if self.gender == 'M':
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
        else:
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161
        return round(bmr)

    @property
    def daily_calories(self):
        """Estimate daily calories needed (BMR * activity factor)"""
        activity_factor = 1.375  # Assuming light exercise
        return round(self.calculate_bmr * activity_factor)

    @property
    def daily_protein_needs(self):
        """Recommended protein intake (2g per kg of body weight)"""
        return round(self.weight * 2)

    @property
    def daily_fat_needs(self):
        """Recommended fat intake (30% of daily calories)"""
        return round((self.daily_calories * 0.3) / 9)  # 9 calories per gram of fat

    @property
    def daily_carbs_needs(self):
        """Remaining calories from carbs (50% of daily calories)"""
        return round((self.daily_calories * 0.5) / 4)  # 4 calories per gram of carbs

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            height=170,  # Default height in cm
            weight=70,   # Default weight in kg
            age=25,      # Default age
            gender='M'   # Default gender
        )
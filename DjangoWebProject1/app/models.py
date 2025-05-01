from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

class FoodItem(models.Model):
    CATEGORY_CHOICES = (
        ('fast_food', 'Фастфуд'),
        ('fruits', 'Фрукти'),
        ('vegetables', 'Овочі'),
        ('meat', "М'ясо"),
        ('dairy', 'Молочні продукти'),
        ('grains', 'Крупи'),
        ('sweets', 'Солодощі'),
        ('drinks', 'Напої'),
        ('other', 'Інше'),
    )
    
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    calories_per_100g = models.FloatField()
    proteins_per_100g = models.FloatField(default=0)
    carbohydrates_per_100g = models.FloatField(default=0)
    fats_per_100g = models.FloatField(default=0)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')

    def __str__(self):
        return f"{self.name} ({self.manufacturer}) - {self.calories_per_100g:.0f} ккал/100г"

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
    
    # Add new field
    ACTIVITY_CHOICES = (
        (1.2, 'Малорухливий спосіб життя, відсутність фізичних навантажень'),
        (1.375, 'Легка активність (легкі тренування 1-3 рази на тиждень)'),
        (1.55, 'Помірна активність (помірні тренування 3-5 разів на тиждень)'),
        (1.725, 'Висока активність (інтенсивні тренування 6-7 разів на тиждень)'),
        (1.9, 'Дуже висока активність (важкі фізичні навантаження, тренування 2 рази на день)'),
    )
    activity_level = models.FloatField(
        choices=ACTIVITY_CHOICES, 
        default=1.375,
        help_text="Виберіть рівень вашої фізичної активності"
    )

    WEIGHT_GOAL_CHOICES = (
        (-1.0, 'Схуднути на 1 кг/тиждень'),
        (-0.5, 'Схуднути на 0.5 кг/тиждень'),
        (0, 'Підтримувати вагу'),
        (0.5, 'Набрати 0.5 кг/тиждень'),
        (1.0, 'Набрати 1 кг/тиждень'),
    )
    weight_goal = models.FloatField(
        choices=WEIGHT_GOAL_CHOICES,
        default=0,
        help_text="Оберіть ціль зміни ваги"
    )

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
        """Calculate daily calories based on BMR, activity and weight goal"""
        maintenance_calories = self.calculate_bmr * self.activity_level
        # Calculate calories adjustment for weight goal
        daily_adjustment = (self.weight_goal * 7700) / 7
        
        total_calories = maintenance_calories + daily_adjustment
        
        # Ensure minimum healthy calories (1200 for women, 1500 for men)
        min_calories = 1200 if self.gender == 'F' else 1500
        return max(round(total_calories), min_calories)

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
            height=170,
            weight=70,
            age=25,
            gender='M',
            activity_level=1.375,
            weight_goal=0
        )

@receiver([post_save, post_delete], sender=FoodItemLog)
def clear_food_log_cache(sender, instance, **kwargs):
    """Clear cache when food log is saved or deleted"""
    # Clear specific day cache
    cache.delete(f'food_logs_{instance.user.id}_{instance.date}')
    cache.delete(f'totals_{instance.user.id}_{instance.date}')
    
    # Clear calendar cache for the affected month
    cache.delete(f'calendar_data_{instance.user.id}_{instance.date.year}_{instance.date.month}')
    
    # Clear recommendations
    cache.delete(f'recommendations_{instance.user.id}')

@receiver([post_save], sender=Profile)
def clear_profile_cache(sender, instance, **kwargs):
    """Clear user-related cache when profile is updated"""
    cache.delete_pattern(f'*_{instance.user.id}_*')

class PendingFoodItem(models.Model):
    CATEGORY_CHOICES = (
        ('fast_food', 'Фастфуд'),
        ('fruits', 'Фрукти'),
        ('vegetables', 'Овочі'),
        ('meat', "М'ясо"),
        ('dairy', 'Молочні продукти'),
        ('grains', 'Крупи'),
        ('sweets', 'Солодощі'),
        ('drinks', 'Напої'),
        ('other', 'Інше'),
    )
    
    category = models.CharField(max_length=20, choices=FoodItem.CATEGORY_CHOICES, default='other')
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    calories_per_100g = models.FloatField()
    proteins_per_100g = models.FloatField(default=0)
    carbohydrates_per_100g = models.FloatField(default=0)
    fats_per_100g = models.FloatField(default=0)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_date = models.DateTimeField(auto_now_add=True)
    votes_to_approve = models.ManyToManyField(User, related_name='voted_approve_pending_foods', blank=True)
    votes_to_reject = models.ManyToManyField(User, related_name='voted_reject_pending_foods', blank=True)

    def __str__(self):
        return f"{self.name} ({self.manufacturer}) - За: {self.votes_to_approve.count()}, Проти: {self.votes_to_reject.count()}"
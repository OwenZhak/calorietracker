"""
Definition of views.
"""

from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from dal import autocomplete
from .models import FoodItemLog, FoodItem, Profile
from .forms import FoodItemLogForm, EditFoodItemLogForm, ProfileForm
import unicodedata
from calendar import monthrange
import calendar as cal

class FoodItemAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            print("User not authenticated")
            return FoodItem.objects.none()

        qs = FoodItem.objects.all()

        if self.q:
            search_term = self.q.lower()  # Convert to lowercase

            def normalize_string(s):
                return unicodedata.normalize('NFKC', s).lower()

            normalized_search_term = normalize_string(search_term)

            qs = [
                item for item in qs
                if normalize_string(item.name).startswith(normalized_search_term) or normalize_string(item.manufacturer).find(normalized_search_term) != -1
            ]
        else:
            # If no search term is provided, return all FoodItem objects
            qs = list(qs)

        return qs

@login_required
def log_food(request: HttpRequest):
    selected_date_str = request.GET.get('date')
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if selected_date_str else datetime.now().date()
    previous_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    year = datetime.now().year

    if request.method == 'POST':
        form = FoodItemLogForm(request.POST)
        if form.is_valid():
            food_item_log = form.save(commit=False)
            food_item_log.user = request.user
            food_item_log.date = selected_date
            food_item_log.save()
            return redirect(f'/log_food/?date={selected_date.strftime("%Y-%m-%d")}')
    else:
        form = FoodItemLogForm()

    food_item_logs = FoodItemLog.objects.filter(user=request.user, date=selected_date)
    total_calories = sum(log.total_calories for log in food_item_logs)
    total_proteins = sum(log.total_proteins for log in food_item_logs)
    total_carbohydrates = sum(log.total_carbohydrates for log in food_item_logs)
    total_fats = sum(log.total_fats for log in food_item_logs)
    
    # Add these lines
    recommended_calories = request.user.profile.daily_calories
    recommended_proteins = request.user.profile.daily_protein_needs
    recommended_carbs = request.user.profile.daily_carbs_needs
    recommended_fats = request.user.profile.daily_fat_needs
    remaining_calories = recommended_calories - total_calories

    context = {
        'form': form,
        'food_item_logs': food_item_logs,
        'selected_date': selected_date,
        'previous_date': previous_date.strftime('%Y-%m-%d'),
        'next_date': next_date.strftime('%Y-%m-%d'),
        'total_calories': total_calories,
        'total_proteins': total_proteins,
        'total_carbohydrates': total_carbohydrates,
        'total_fats': total_fats,
        'recommended_calories': recommended_calories,
        'recommended_proteins': recommended_proteins,
        'recommended_carbs': recommended_carbs,
        'recommended_fats': recommended_fats,
        'remaining_calories': remaining_calories,
        'login_required': not request.user.is_authenticated,
        'year': year,
    }
    return render(request, 'app/log_food.html', context)

@login_required
def edit_food_log(request, log_id):
    log_entry = get_object_or_404(FoodItemLog, id=log_id, user=request.user)

    if request.method == 'POST':
        form = EditFoodItemLogForm(request.POST, instance=log_entry)
        if form.is_valid():
            form.save()
            selected_date = log_entry.date.strftime('%Y-%m-%d')
            return redirect(f'/log_food/?date={selected_date}')
    else:
        form = EditFoodItemLogForm(instance=log_entry)

    return render(
        request,
        'app/edit_food_log.html',
        {
            'title': 'Edit Food Log',
            'form': form,
            'log_entry': log_entry,
            'year': datetime.now().year,
        }
    )

@login_required
def calendar(request):
    year = request.GET.get('year', datetime.now().year)
    month = request.GET.get('month', datetime.now().month)
    year, month = int(year), int(month)
    
    first_day_of_month, days_in_month = monthrange(year, month)
    dates = [datetime(year, month, day) for day in range(1, days_in_month + 1)]
    
    calendar_data = []
    for date in dates:
        food_logs = FoodItemLog.objects.filter(user=request.user, date=date)
        total_calories = sum(log.total_calories for log in food_logs)
        calendar_data.append({
            'date': date,
            'calories': total_calories
        })
    
    month_name = cal.month_name[month]
    
    context = {
        'year': year,
        'month': month_name,
        'calendar_data': calendar_data,
        'previous_month': (month - 1) if month > 1 else 12,
        'previous_year': year if month > 1 else year - 1,
        'next_month': (month + 1) if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
    }
    
    return render(request, 'app/calendar.html', context)

def custom_logout(request):
    """Logs out the user and redirects to the home page."""
    logout(request)
    return redirect('/')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'app/register.html', {'form': form})

@login_required
def profile(request):
    profile_obj, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'height': 170,
            'weight': 70,
            'age': 25,
            'gender': 'M',
            'activity_level': 1.375,
            'weight_goal': 0
        }
    )

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj)

    context = {
        'form': form,
        'profile': profile_obj,
        'year': datetime.now().year,
    }
    return render(request, 'app/profile.html', context)

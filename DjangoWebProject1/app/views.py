"""
Definition of views.
"""

from datetime import datetime, timedelta
from django.db.models import Sum, Count
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from dal import autocomplete
from .models import FoodItemLog, FoodItem, Profile, PendingFoodItem
from .forms import FoodItemLogForm, EditFoodItemLogForm, ProfileForm, PendingFoodItemForm
import unicodedata
from calendar import monthrange
import calendar as cal
from django.contrib import messages

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
def log_food(request):
    # First ensure user has a profile
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

    # Get the selected date
    selected_date = request.GET.get('date', datetime.now().date())
    if isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    # Handle form submission
    if request.method == 'POST':
        form = FoodItemLogForm(request.POST)
        if form.is_valid():
            food_log = form.save(commit=False)
            food_log.user = request.user
            food_log.date = selected_date
            food_log.save()
            return redirect(f'/log_food/?date={selected_date.strftime("%Y-%m-%d")}')
    else:
        form = FoodItemLogForm()

    # Calculate next and previous dates
    next_date = selected_date + timedelta(days=1)
    previous_date = selected_date - timedelta(days=1)

    # Get food logs for the selected date
    food_item_logs = FoodItemLog.objects.filter(user=request.user, date=selected_date)
    total_calories = sum(log.total_calories for log in food_item_logs)
    total_proteins = sum(log.total_proteins for log in food_item_logs)
    total_carbohydrates = sum(log.total_carbohydrates for log in food_item_logs)
    total_fats = sum(log.total_fats for log in food_item_logs)

    recommended_calories = profile_obj.daily_calories
    recommended_proteins = profile_obj.daily_protein_needs
    recommended_carbs = profile_obj.daily_carbs_needs
    recommended_fats = profile_obj.daily_fat_needs
    remaining_calories = recommended_calories - total_calories

    context = {
        'form': form,  # Changed from FoodItemLogForm to form instance
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
        'year': selected_date.year,
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


@login_required
def submit_food(request):
    if request.method == 'POST':
        form = PendingFoodItemForm(request.POST)
        if form.is_valid():
            pending_food = form.save(commit=False)
            pending_food.submitted_by = request.user
            pending_food.save()
            messages.success(request, 'Продукт додано на розгляд. Дякуємо за внесок!')
            return redirect('log_food')
    else:
        form = PendingFoodItemForm()
    
    return render(request, 'app/submit_food.html', {'form': form})

@login_required
def pending_foods(request):
    pending_items = PendingFoodItem.objects.filter(status='pending')
    return render(request, 'app/pending_foods.html', {
        'pending_items': pending_items,
    })


@login_required
def review_foods(request):
    # Get all pending food items
    pending_items = PendingFoodItem.objects.all()
    return render(request, 'app/review_foods.html', {'pending_items': pending_items})

@login_required
def approve_food(request, food_id):
    if request.method == 'POST':
        pending_food = get_object_or_404(PendingFoodItem, id=food_id)
        
        # Check if user is the creator
        if pending_food.submitted_by == request.user:
            messages.warning(request, 'Ви не можете голосувати за власний продукт.')
            return redirect('review_foods')
            
        # Check if user has already voted to reject
        if request.user in pending_food.votes_to_reject.all():
            messages.warning(request, 'Ви вже проголосували проти цього продукту.')
            return redirect('review_foods')
        
        # Check if user hasn't already voted to approve
        if request.user not in pending_food.votes_to_approve.all():
            pending_food.votes_to_approve.add(request.user)
            pending_food.save()
            
            if pending_food.votes_to_approve.count() >= 3:
                FoodItem.objects.create(
                    name=pending_food.name,
                    manufacturer=pending_food.manufacturer,
                    calories_per_100g=pending_food.calories_per_100g,
                    proteins_per_100g=pending_food.proteins_per_100g,
                    carbohydrates_per_100g=pending_food.carbohydrates_per_100g,
                    fats_per_100g=pending_food.fats_per_100g
                )
                pending_food.delete()
                messages.success(request, f'Продукт "{pending_food.name}" додано до бази даних.')
            else:
                messages.info(request, f'Ваш голос "за" зараховано. Потрібно ще {3 - pending_food.votes_to_approve.count()} голосів.')
        else:
            messages.warning(request, 'Ви вже проголосували за цей продукт.')
            
    return redirect('review_foods')

@login_required
def reject_food(request, food_id):
    if request.method == 'POST':
        pending_food = get_object_or_404(PendingFoodItem, id=food_id)
        
        # Check if user is the creator
        if pending_food.submitted_by == request.user:
            messages.warning(request, 'Ви не можете голосувати за власний продукт.')
            return redirect('review_foods')
            
        # Check if user has already voted to approve
        if request.user in pending_food.votes_to_approve.all():
            messages.warning(request, 'Ви вже проголосували за цей продукт.')
            return redirect('review_foods')
        
        # Check if user hasn't already voted to reject
        if request.user not in pending_food.votes_to_reject.all():
            pending_food.votes_to_reject.add(request.user)
            pending_food.save()
            
            if pending_food.votes_to_reject.count() >= 3:
                name = pending_food.name
                pending_food.delete()
                messages.warning(request, f'Продукт "{name}" відхилено.')
            else:
                messages.info(request, f'Ваш голос "проти" зараховано. Потрібно ще {3 - pending_food.votes_to_reject.count()} голосів.')
        else:
            messages.warning(request, 'Ви вже проголосували проти цього продукту.')
            
    return redirect('review_foods')

@login_required
def recommendations(request):
    # Get logs from the last 3 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=3)
    
    # Get user's food logs
    food_logs = FoodItemLog.objects.filter(
        user=request.user,
        date__range=(start_date, end_date)
    ).select_related('food_item')

    # Check if we have any logs
    if not food_logs.exists():
        context = {
            'no_data': True,
            'message': 'Для отримання рекомендацій потрібно додати більше записів про харчування.',
            'sub_message': 'Додайте кілька прийомів їжі, і ми зможемо надати вам персоналізовані поради щодо харчування.'
        }
        return render(request, 'app/recommendations.html', context)

    # Analyze eating habits
    recommendations = []
    category_counts = defaultdict(int)
    category_calories = defaultdict(float)
    
    # Calculate totals per category
    for log in food_logs:
        category = log.food_item.category
        category_counts[category] += 1
        category_calories[category] += log.total_calories

    # Generate recommendations
    if category_calories['fast_food'] > 500:
        recommendations.append({
            'type': 'warning',
            'message': 'Ви споживаєте забагато фастфуду. Спробуйте замінити його на здоровішу їжу.',
            'suggestions': ['овочі', 'фрукти', 'цільнозернові продукти']
        })

    if category_counts['vegetables'] < 2:
        recommendations.append({
            'type': 'suggestion',
            'message': 'Додайте більше овочів до свого раціону для збалансованого харчування.',
            'suggestions': ['салат', 'броколі', 'морква']
        })

    if category_calories['sweets'] > 300:
        recommendations.append({
            'type': 'warning',
            'message': 'Високе споживання солодощів. Спробуйте замінити їх на фрукти.',
            'suggestions': ['яблука', 'груші', 'ягоди']
        })

    context = {
        'recommendations': recommendations,
        'category_calories': dict(category_calories),
        'category_counts': dict(category_counts),
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'app/recommendations.html', context)

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
from .models import FoodItemLog, FoodItem
from .forms import FoodItemLogForm, EditFoodItemLogForm
import unicodedata

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

    return render(
        request,
        'app/log_food.html',
        {
            'form': form,
            'food_item_logs': food_item_logs,
            'selected_date': selected_date,
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'next_date': next_date.strftime('%Y-%m-%d'),
            'total_calories': total_calories,
            'login_required': not request.user.is_authenticated,
            'year': year,
        }
    )

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


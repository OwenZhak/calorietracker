"""
Definition of views.
"""

from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from .models import FoodItemLog
from .forms import FoodItemLogForm

def log_food(request):
    """Renders the log food page."""
    assert isinstance(request, HttpRequest)
    
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('log_food')
        else:
            form = AuthenticationForm()
        return render(
            request,
            'app/log_food.html',
            {
                'title': 'Log Food',
                'form': form,
                'login_required': True,
                'year': datetime.now().year,
            }
        )
    
    # Handle date navigation
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()
    
    if request.method == 'POST':
        form = FoodItemLogForm(request.POST)
        if form.is_valid():
            food_item_log = form.save(commit=False)
            food_item_log.user = request.user
            food_item_log.date = selected_date  # Set the date to the selected date
            food_item_log.save()
            return redirect(f'{request.path}?date={selected_date.strftime("%Y-%m-%d")}')
    else:
        form = FoodItemLogForm()
    
    food_item_logs = FoodItemLog.objects.filter(user=request.user, date=selected_date)
    total_calories = sum(log.total_calories for log in food_item_logs)
    
    previous_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    
    return render(
        request,
        'app/log_food.html',
        {
            'title': 'Log Food',
            'form': form,
            'food_item_logs': food_item_logs,
            'total_calories': total_calories,
            'selected_date': selected_date,
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'next_date': next_date.strftime('%Y-%m-%d'),
            'year': datetime.now().year,
        }
    )

def custom_logout(request):
    """Logs out the user and redirects to the home page."""
    logout(request)
    return redirect('log_food')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('log_food')
    else:
        form = UserCreationForm()
    return render(request, 'app/register.html', {'form': form})

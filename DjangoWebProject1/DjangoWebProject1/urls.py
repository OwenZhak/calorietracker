from datetime import datetime
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth.views import LoginView
from app import forms, views

urlpatterns = [
    path('', views.log_food, name='log_food'),
    path('login/', LoginView.as_view(template_name='app/login.html', authentication_form=forms.BootstrapAuthenticationForm, extra_context={'title': 'Log in', 'year': datetime.now().year}), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('admin/', admin.site.urls),
    path('log_food/', views.log_food, name='log_food'),
    path('register/', views.register, name='register'),
    path('edit_food_log/<int:log_id>/', views.edit_food_log, name='edit_food_log'),
    path(
        'fooditem-autocomplete/',
        views.FoodItemAutocomplete.as_view(),
        name='fooditem-autocomplete',
    ),  # Add this line
]
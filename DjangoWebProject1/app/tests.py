"""
Tests for Django application views
"""

import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile, FoodItemLog, FoodItem, PendingFoodItem
from django.utils import timezone


class ViewTest(TestCase):
    """Tests for the application views."""

    @classmethod
    def setUpClass(cls):
        super(ViewTest, cls).setUpClass()
        django.setup()

    def setUp(self):
        # Create test user
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)


    def test_log_food_authenticated(self):
        """Test log food page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('log_food'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/log_food.html')

    def test_log_food_unauthenticated(self):
        """Test log food page redirects for unauthenticated user"""
        response = self.client.get(reverse('log_food'))
        self.assertEqual(response.status_code, 302)
        expected_url = '/login/?next=/log_food/'
        self.assertRedirects(response, expected_url)

    def test_profile_view(self):
        """Test profile view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/profile.html')

    def test_food_log_create(self):
        """Test creating a food log entry"""
        self.client.login(username='testuser', password='testpass123')
        
        # First create a FoodItem
        food_item = FoodItem.objects.create(
            name='Apple',  
            manufacturer='Nature',
            calories_per_100g=52,
            proteins_per_100g=0.3,
            carbohydrates_per_100g=14,
            fats_per_100g=0.2
        )
        
        data = {
            'food_item': food_item.id,
            'quantity_in_grams': 100,
            'date': timezone.now().date()
        }
        
        response = self.client.post(reverse('log_food'), data)
        # Changed expectation to 302 since view redirects after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check if FoodItemLog was created with the correct food_item
        self.assertTrue(
            FoodItemLog.objects.filter(
                food_item=food_item,
                user=self.user
            ).exists()
        )

    def test_calendar_view(self):
        """Test calendar view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/calendar.html')

    def test_register_view(self):
        """Test registration view"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/register.html')

    def test_submit_food_authenticated(self):
        """Test submitting new food item"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'Test Food',
            'manufacturer': 'Test Company',
            'category': 'other',
            'calories_per_100g': 100,
            'proteins_per_100g': 5,
            'carbohydrates_per_100g': 15,
            'fats_per_100g': 3
        }
        response = self.client.post(reverse('submit_food'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.assertTrue(PendingFoodItem.objects.filter(name='Test Food').exists())

    def test_edit_food_log(self):
        """Test editing existing food log entry"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create initial food log entry
        food_item = FoodItem.objects.create(
            name='Initial Food',
            manufacturer='Test',
            calories_per_100g=100
        )
        food_log = FoodItemLog.objects.create(
            user=self.user,
            food_item=food_item,
            quantity_in_grams=100,
            date=timezone.now().date()
        )
        
        # Edit data
        edit_data = {
            'food_item': food_item.id,
            'quantity_in_grams': 200
        }
        
        response = self.client.post(
            reverse('edit_food_log', kwargs={'log_id': food_log.id}),
            edit_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify changes
        updated_log = FoodItemLog.objects.get(id=food_log.id)
        self.assertEqual(updated_log.quantity_in_grams, 200)

    def test_recommendations_view(self):
        """Test recommendations view with food logs"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create some food logs
        food_item = FoodItem.objects.create(
            name='Test Food',
            manufacturer='Test',
            calories_per_100g=100,
            category='vegetables'
        )
        FoodItemLog.objects.create(
            user=self.user,
            food_item=food_item,
            quantity_in_grams=100,
            date=timezone.now().date()
        )
        
        response = self.client.get(reverse('recommendations'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/recommendations.html')

    def test_profile_update(self):
        """Test updating user profile"""
        self.client.login(username='testuser', password='testpass123')
        
        update_data = {
            'height': 180,
            'weight': 75,
            'age': 30,
            'gender': 'M',
            'activity_level': 1.55,
            'weight_goal': 0
        }
        
        response = self.client.post(reverse('profile'), update_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify profile updates
        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.height, 180)
        self.assertEqual(updated_profile.weight, 75)
        self.assertEqual(updated_profile.age, 30)

    def test_register_user_creation(self):
        """Test user registration creates profile"""
        data = {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        
        # Verify user and profile creation
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_food_log_create_invalid_data(self):
        """Test creating a food log entry with invalid data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'food_item': 999,  # Non-existent food item
            'quantity_in_grams': -100,  # Invalid quantity
            'date': timezone.now().date()
        }
        
        response = self.client.post(reverse('log_food'), data)
        self.assertEqual(response.status_code, 200)  # Returns to form
        self.assertTrue(response.context['form'].errors)  # Should have form errors

    def test_submit_food_invalid_data(self):
        """Test submitting food item with invalid data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'name': '',  # Empty name
            'manufacturer': 'Test Company',
            'category': 'invalid_category',  # Invalid category
            'calories_per_100g': -100,  # Invalid calories
            'proteins_per_100g': -5,
            'carbohydrates_per_100g': -15,
            'fats_per_100g': -3
        }
        
        response = self.client.post(reverse('submit_food'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_profile_update_invalid_data(self):
        """Test profile update with invalid data"""
        self.client.login(username='testuser', password='testpass123')
        
        update_data = {
            'height': -180,  # Invalid height
            'weight': -75,   # Invalid weight
            'age': -30,      # Invalid age
            'gender': 'X',   # Invalid gender
            'activity_level': 0,  # Invalid activity level
            'weight_goal': 99     # Invalid weight goal
        }
        
        response = self.client.post(reverse('profile'), update_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_delete_food_log(self):
        """Test deleting a food log entry"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a food log entry
        food_item = FoodItem.objects.create(
            name='Test Food',
            manufacturer='Test',
            calories_per_100g=100
        )
        food_log = FoodItemLog.objects.create(
            user=self.user,
            food_item=food_item,
            quantity_in_grams=100,
            date=timezone.now().date()
        )
        
        # Delete the entry
        response = self.client.post(reverse('delete_food_log', kwargs={'log_id': food_log.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FoodItemLog.objects.filter(id=food_log.id).exists())

    def test_date_based_food_logs(self):
        """Test viewing food logs for specific dates"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create food logs for different dates
        food_item = FoodItem.objects.create(
            name='Test Food',
            manufacturer='Test',
            calories_per_100g=100
        )
        
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        FoodItemLog.objects.create(
            user=self.user,
            food_item=food_item,
            quantity_in_grams=100,
            date=today
        )
        
        FoodItemLog.objects.create(
            user=self.user,
            food_item=food_item,
            quantity_in_grams=100,
            date=yesterday
        )
        
        # Test today's logs
        response = self.client.get(reverse('log_food'), {'date': today})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['food_item_logs']), 1)  # Changed from food_logs to food_item_logs
        
        # Test yesterday's logs
        response = self.client.get(reverse('log_food'), {'date': yesterday})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['food_item_logs']), 1)  # Changed from food_logs to food_item_logs

    def test_unauthorized_access(self):
        """Test unauthorized access to other user's data"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        
        # Create food log for other user
        food_item = FoodItem.objects.create(
            name='Other Food',
            manufacturer='Test',
            calories_per_100g=100
        )
        
        food_log = FoodItemLog.objects.create(
            user=other_user,
            food_item=food_item,
            quantity_in_grams=100,
            date=timezone.now().date()
        )
        
        # Try to access other user's food log
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('edit_food_log', kwargs={'log_id': food_log.id})
        )
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.user.delete()
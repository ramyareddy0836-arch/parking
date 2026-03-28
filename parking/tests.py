from django.test import TestCase
from django.contrib.auth import get_user_model
from .views import CustomUserCreationForm

User = get_user_model()

class UserAuthenticationTest(TestCase):
    def test_registration_valid(self):
        data = {
            'username': 'john_doe_123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, 'john_doe_123')
        self.assertEqual(user.email, 'john@example.com')

    def test_registration_name_with_space(self):
        data = {
            'username': 'johndoe',
            'first_name': 'John Paul',
            'last_name': 'Van Doe',
            'email': 'john3@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_registration_invalid_password_length(self):
        data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'Pass1!',
            'password2': 'Pass1!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(any('password' in key for key in form.errors))

    def test_registration_invalid_password_no_upper(self):
        data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'password123!',
            'password2': 'password123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_registration_invalid_password_no_special(self):
        data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'Password123',
            'password2': 'Password123'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_registration_invalid_name(self):
        data = {
            'username': 'newuser',
            'first_name': 'John123',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_registration_duplicate_email(self):
        User.objects.create_user(username='olduser', email='john@example.com', password='Password123!')
        data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_registration_invalid_username(self):
        data = {
            'username': 'user!@#',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john2@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_registration_username_with_period(self):
        data = {
            'username': 'ramya.123',
            'first_name': 'Ramya',
            'last_name': 'Reddy',
            'email': 'ramya@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_registration_username_too_short(self):
        data = {
            'username': 'ram',
            'first_name': 'Ramya',
            'last_name': 'Reddy',
            'email': 'ramya@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_registration_name_too_short(self):
        data = {
            'username': 'ramya',
            'first_name': 'R',
            'last_name': 'Reddy',
            'email': 'ramya@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_registration_password_complexity(self):
        # No lowercase
        data = {
            'username': 'ramya',
            'first_name': 'Ramya',
            'last_name': 'Reddy',
            'email': 'ramya@example.com',
            'password1': 'PASSWORD123!',
            'password2': 'PASSWORD123!'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        
        # No number
        data['password1'] = 'Password!'
        data['password2'] = 'Password!'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_dual_login(self):
        # Create a user
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='Password123!',
            first_name='Test',
            last_name='User'
        )
        
        # Test login with username
        login_success = self.client.login(username='testuser', password='Password123!')
        self.assertTrue(login_success)
        self.client.logout()

        # Test login with email
        login_success = self.client.login(username='test@example.com', password='Password123!')
        self.assertTrue(login_success)

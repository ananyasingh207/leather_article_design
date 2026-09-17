from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AuthenticationFlowTestCase(TestCase):
    """
    Test suite for Phase 2 User Authentication in LeatherCraft Designer.
    """

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.dashboard_url = reverse('dashboard')
        self.profile_url = reverse('profile')

        self.test_user_password = 'CraftPassword123!'
        self.test_user = User.objects.create_user(
            username='artisan_john',
            email='john@leathercraft.com',
            password=self.test_user_password,
            first_name='John Miller'
        )

    def test_registration_get_page(self):
        """Test GET request to register page renders properly."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertContains(response, 'Create an Account')

    def test_registration_success_and_auto_login(self):
        """Test user registration creates user in DB, logs in, and redirects to dashboard."""
        data = {
            'name': 'Sarah Vance',
            'email': 'sarah@leathercraft.com',
            'password': 'SecureLeather2026!',
            'confirm_password': 'SecureLeather2026!'
        }
        response = self.client.post(self.register_url, data, follow=True)
        self.assertRedirects(response, self.dashboard_url)
        
        # Verify DB entry
        user = User.objects.filter(email='sarah@leathercraft.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'Sarah Vance')
        self.assertTrue(user.check_password('SecureLeather2026!'))

        # Verify authenticated session
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.assertContains(response, 'Welcome, Sarah Vance!')

    def test_registration_duplicate_email_fails(self):
        """Test that duplicate email is rejected with a validation error."""
        data = {
            'name': 'Another John',
            'email': 'john@leathercraft.com',  # existing email
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An account with this email address already exists.')
        # Ensure second user is not created
        self.assertEqual(User.objects.filter(email='john@leathercraft.com').count(), 1)

    def test_registration_password_mismatch_fails(self):
        """Test that non-matching password confirmation fails validation."""
        data = {
            'name': 'Mismatch User',
            'email': 'mismatch@leathercraft.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword456!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match.')

    def test_login_success_with_email(self):
        """Test logging in with email and password creates session and redirects to dashboard."""
        data = {
            'email': 'john@leathercraft.com',
            'password': self.test_user_password
        }
        response = self.client.post(self.login_url, data, follow=True)
        self.assertRedirects(response, self.dashboard_url)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.test_user.pk)
        self.assertContains(response, 'Welcome, John Miller!')

    def test_login_invalid_credentials(self):
        """Test invalid email or password shows error message."""
        data = {
            'email': 'john@leathercraft.com',
            'password': 'WrongPassword999!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password.')

    def test_logout_clears_session(self):
        """Test logout clears session and redirects to home."""
        self.client.force_login(self.test_user)
        response = self.client.get(self.logout_url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, 'You have been logged out.')

    def test_dashboard_access_protection_unauthenticated(self):
        """Test unauthenticated access to /dashboard/ redirects to /login/?next=/dashboard/."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_dashboard_access_authenticated(self):
        """Test authenticated user accesses dashboard successfully."""
        self.client.force_login(self.test_user)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'Welcome, John Miller!')
        self.assertContains(response, 'My Designs')
        self.assertContains(response, 'Saved Articles')

    def test_profile_access_protection_and_display(self):
        """Test profile page access and details display."""
        # Unauthenticated
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

        # Authenticated
        self.client.force_login(self.test_user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response, 'John Miller')
        self.assertContains(response, 'john@leathercraft.com')
        self.assertContains(response, 'artisan_john')

    def test_authenticated_user_redirect_from_login_and_register(self):
        """Test that logged-in users are redirected to dashboard if visiting /login/ or /register/."""
        self.client.force_login(self.test_user)
        
        response_login = self.client.get(self.login_url)
        self.assertRedirects(response_login, self.dashboard_url)

        response_register = self.client.get(self.register_url)
        self.assertRedirects(response_register, self.dashboard_url)


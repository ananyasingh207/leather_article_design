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


from decimal import Decimal
from articles.models import Article
from designs.models import Design


class StaffAdminDashboardTestCase(TestCase):
    """
    Phase 10 Test Suite:
    Validates staff-only admin dashboard access permissions, summary counts,
    recent records display, Django built-in admin links, and navigation visibility.
    """

    def setUp(self):
        self.client = Client()
        self.admin_dashboard_url = reverse('admin_dashboard')
        self.staff_dashboard_url = reverse('staff_dashboard')

        # Create ordinary artisan user
        self.ordinary_user = User.objects.create_user(
            username='artisan_bob',
            email='bob@leathercraft.com',
            password='Password123!',
            first_name='Bob Artisan',
            is_staff=False
        )

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff_alice',
            email='alice@leathercraft.com',
            password='StaffPassword123!',
            first_name='Alice Manager',
            is_staff=True
        )

        # Create sample articles
        self.article_1 = Article.objects.create(
            name='Luxury Leather Briefcase',
            category=Article.CATEGORY_HANDBAGS,
            description='Handmade Italian leather briefcase with brass fittings.',
            material='Full Grain Leather',
            base_price=Decimal('12500.00')
        )
        self.article_2 = Article.objects.create(
            name='Artisan Minimalist Wallet',
            category=Article.CATEGORY_WALLETS,
            description='Slim bifold wallet with RFID shielding.',
            material='Top Grain Leather',
            base_price=Decimal('1800.00')
        )

        # Create sample design
        self.design_1 = Design.objects.create(
            user=self.ordinary_user,
            article=self.article_1,
            name='Executive Briefcase Custom',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_DARK_BROWN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('38.0'),
            height=Decimal('28.0'),
            depth=Decimal('9.0'),
            stitching_color=Design.STITCH_BROWN,
            custom_text='B.A.',
            font=Design.FONT_CLASSIC,
            text_size=18,
        )

    def test_unauthenticated_user_cannot_access_admin_dashboard(self):
        """Test logged-out users are redirected to login and cannot access the admin dashboard."""
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_ordinary_user_access_denied_or_redirected(self):
        """Test ordinary (non-staff) user is denied or redirected away from the admin dashboard."""
        self.client.force_login(self.ordinary_user)
        response = self.client.get(self.admin_dashboard_url)
        # Verify access is denied (403) or redirected (302)
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertTrue(response.url.startswith('/login/'))

    def test_staff_user_can_access_admin_dashboard(self):
        """Test authenticated Django staff user can open the admin dashboard with HTTP 200."""
        self.client.force_login(self.staff_user)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'Staff Admin Dashboard')
        self.assertContains(response, 'Staff Administration')

    def test_staff_dashboard_alias_url_works(self):
        """Test staff_dashboard URL route works for staff users."""
        self.client.force_login(self.staff_user)
        response = self.client.get(self.staff_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')

    def test_summary_counts_match_database(self):
        """Test summary counts accurately match database records."""
        self.client.force_login(self.staff_user)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)

        # Verify context values
        total_users = User.objects.count()
        total_articles = Article.objects.count()
        total_designs = Design.objects.count()

        self.assertEqual(response.context['total_users_count'], total_users)
        self.assertEqual(response.context['total_articles_count'], total_articles)
        self.assertEqual(response.context['total_designs_count'], total_designs)

        # Verify counts in HTML
        self.assertContains(response, f'id="count-total-users">{total_users}</div>')
        self.assertContains(response, f'id="count-total-articles">{total_articles}</div>')
        self.assertContains(response, f'id="count-total-designs">{total_designs}</div>')

    def test_recent_records_display_correct_details(self):
        """Test recent users, articles, and designs display with expected details."""
        self.client.force_login(self.staff_user)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)

        # Users check
        self.assertContains(response, 'Bob Artisan')
        self.assertContains(response, 'bob@leathercraft.com')
        self.assertContains(response, 'Alice Manager')
        self.assertContains(response, 'alice@leathercraft.com')

        # Articles check
        self.assertContains(response, 'Luxury Leather Briefcase')
        self.assertContains(response, 'Full Grain Leather')
        self.assertContains(response, '12500.00')
        self.assertContains(response, 'Artisan Minimalist Wallet')

        # Designs check
        self.assertContains(response, 'Executive Briefcase Custom')
        self.assertContains(response, 'Dark Brown')

    def test_admin_console_links_present(self):
        """Test links to Django's built-in /admin/ are present on the dashboard."""
        self.client.force_login(self.staff_user)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, reverse('admin:index'))
        self.assertContains(response, reverse('admin:auth_user_changelist'))
        self.assertContains(response, reverse('admin:articles_article_changelist'))
        self.assertContains(response, reverse('admin:designs_design_changelist'))
        self.assertContains(response, reverse('admin:auth_user_change', args=[self.ordinary_user.id]))
        self.assertContains(response, reverse('admin:articles_article_change', args=[self.article_1.id]))
        self.assertContains(response, reverse('admin:designs_design_change', args=[self.design_1.id]))

    def test_navigation_bar_staff_link_visibility(self):
        """Test Admin Dashboard link in navbar is only visible to staff users."""
        # 1. Unauthenticated: no admin dashboard nav link
        resp_anon = self.client.get(reverse('home'))
        self.assertNotContains(resp_anon, 'id="nav-link-admin-dashboard"')

        # 2. Ordinary user: no admin dashboard nav link
        self.client.force_login(self.ordinary_user)
        resp_user = self.client.get(reverse('dashboard'))
        self.assertNotContains(resp_user, 'id="nav-link-admin-dashboard"')
        self.assertNotContains(resp_user, 'id="btn-staff-admin-dashboard"')

        # 3. Staff user: admin dashboard nav link and artisan dashboard button present
        self.client.force_login(self.staff_user)
        resp_staff = self.client.get(reverse('dashboard'))
        self.assertContains(resp_staff, 'id="nav-link-admin-dashboard"')
        self.assertContains(resp_staff, 'id="btn-staff-admin-dashboard"')

    def test_builtin_django_admin_works(self):
        """Test built-in Django /admin/ index remains functional for staff users."""
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django administration')



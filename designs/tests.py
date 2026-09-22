from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from articles.models import Article
from .models import Design
from .forms import DesignForm


class DesignModelTestCase(TestCase):
    """
    Test suite for Design model creation, field validations, and relationships.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='artisan_elena',
            email='elena@craft.com',
            password='TestPassword123!'
        )
        self.article = Article.objects.create(
            name='Classic Leather Wallet',
            category=Article.CATEGORY_WALLETS,
            material='Full Grain Leather',
            base_price=Decimal('500.00'),
            description='Handmade bifold wallet.'
        )

    def test_create_design_instance(self):
        """Test successful creation of a Design instance with all fields."""
        design = Design.objects.create(
            user=self.user,
            article=self.article,
            name='Heritage Bifold Brown',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_BROWN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_BROWN,
            custom_text='ELENA',
            font=Design.FONT_CLASSIC,
            text_size=18
        )
        self.assertEqual(Design.objects.count(), 1)
        self.assertEqual(str(design), 'Heritage Bifold Brown (Classic Leather Wallet) - artisan_elena')
        self.assertEqual(design.user, self.user)
        self.assertEqual(design.article, self.article)
        self.assertEqual(design.width, Decimal('11.5'))

    def test_user_deletion_cascades_design(self):
        """Test that deleting a User cascades and deletes their designs."""
        Design.objects.create(
            user=self.user,
            article=self.article,
            name='Temporary Design',
            leather_type=Design.LEATHER_TYPE_TOP_GRAIN,
            leather_color=Design.COLOR_BLACK,
            leather_finish=Design.FINISH_SMOOTH,
            width=Decimal('10.0'),
            height=Decimal('10.0'),
            depth=Decimal('1.0'),
            stitching_color=Design.STITCH_BLACK,
        )
        self.assertEqual(Design.objects.count(), 1)
        self.user.delete()
        self.assertEqual(Design.objects.count(), 0)

    def test_article_deletion_cascades_design(self):
        """Test that deleting an Article template cleanly removes associated designs."""
        Design.objects.create(
            user=self.user,
            article=self.article,
            name='Article Cascade Test',
            leather_type=Design.LEATHER_TYPE_GENUINE,
            leather_color=Design.COLOR_TAN,
            leather_finish=Design.FINISH_TEXTURED,
            width=Decimal('12.0'),
            height=Decimal('8.0'),
            depth=Decimal('1.5'),
            stitching_color=Design.STITCH_TAN,
        )
        self.assertEqual(Design.objects.count(), 1)
        self.article.delete()
        self.assertEqual(Design.objects.count(), 0)


class DesignFormTestCase(TestCase):
    """
    Test suite for DesignForm validation rules.
    """

    def test_valid_design_form(self):
        """Test that valid input passes form validation."""
        form_data = {
            'name': 'Bespoke Tan Belt',
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,
            'leather_color': Design.COLOR_TAN,
            'leather_finish': Design.FINISH_SMOOTH,
            'width': '110.0',
            'height': '3.8',
            'depth': '0.4',
            'stitching_color': Design.STITCH_TAN,
            'custom_text': 'CRAFT 2026',
            'font': Design.FONT_MODERN,
            'text_size': 20,
        }
        form = DesignForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_name_fails(self):
        """Test that omitting name fails form validation."""
        form_data = {
            'name': '   ',
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,
            'leather_color': Design.COLOR_TAN,
            'leather_finish': Design.FINISH_SMOOTH,
            'width': '10.0',
            'height': '10.0',
            'depth': '1.0',
            'stitching_color': Design.STITCH_BLACK,
            'text_size': 18,
        }
        form = DesignForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_zero_or_negative_dimensions_fail(self):
        """Test that zero or negative dimensions are rejected."""
        form_data = {
            'name': 'Invalid Dimensions Design',
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,
            'leather_color': Design.COLOR_BLACK,
            'leather_finish': Design.FINISH_MATTE,
            'width': '-5.0',
            'height': '0',
            'depth': '-1.0',
            'stitching_color': Design.STITCH_BLACK,
            'text_size': 18,
        }
        form = DesignForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('width', form.errors)
        self.assertIn('height', form.errors)
        self.assertIn('depth', form.errors)


class DesignStudioViewsTestCase(TestCase):
    """
    Test suite for Design Studio views: access control, form submission, ownership security.
    """

    def setUp(self):
        self.client = Client()
        self.user_a = User.objects.create_user(
            username='user_alice',
            email='alice@craft.com',
            password='Password123!'
        )
        self.user_b = User.objects.create_user(
            username='user_bob',
            email='bob@craft.com',
            password='Password123!'
        )
        self.article = Article.objects.create(
            name='Classic Leather Wallet',
            category=Article.CATEGORY_WALLETS,
            material='Full Grain Leather',
            base_price=Decimal('500.00'),
            description='Handcrafted bifold wallet.'
        )

    def test_unauthenticated_create_redirects_to_login(self):
        """Test that unauthenticated GET on design_create redirects to login."""
        url = reverse('design_create', kwargs={'article_id': self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_unauthenticated_detail_redirects_to_login(self):
        """Test that unauthenticated GET on design_detail redirects to login."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.article,
            name='Alice Wallet',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_BROWN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_BROWN,
        )
        url = reverse('design_detail', kwargs={'design_id': design.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_authenticated_user_accesses_design_studio(self):
        """Test that authenticated user can load Design Studio for an article."""
        self.client.force_login(self.user_a)
        url = reverse('design_create', kwargs={'article_id': self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'designs/design_form.html')
        self.assertContains(response, 'Configure &amp; Customize: Classic Leather Wallet')
        self.assertContains(response, '₹500.00')
        self.assertContains(response, 'Live Interactive Preview')

    def test_design_studio_invalid_article_returns_404(self):
        """Test that non-existent article returns 404 in Design Studio."""
        self.client.force_login(self.user_a)
        url = reverse('design_create', kwargs={'article_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create_design_success(self):
        """Test POSTing valid form creates design and redirects to design_detail."""
        self.client.force_login(self.user_a)
        url = reverse('design_create', kwargs={'article_id': self.article.id})
        post_data = {
            'name': 'Alice Custom Dark Brown Wallet',
            'leather_type': Design.LEATHER_TYPE_TOP_GRAIN,
            'leather_color': Design.COLOR_DARK_BROWN,
            'leather_finish': Design.FINISH_SMOOTH,
            'width': '12.0',
            'height': '9.5',
            'depth': '2.2',
            'stitching_color': Design.STITCH_TAN,
            'custom_text': 'ALICE 2026',
            'font': Design.FONT_ELEGANT,
            'text_size': 24,
        }
        response = self.client.post(url, post_data)
        self.assertEqual(Design.objects.count(), 1)
        created_design = Design.objects.first()
        self.assertEqual(created_design.name, 'Alice Custom Dark Brown Wallet')
        self.assertEqual(created_design.user, self.user_a)
        self.assertEqual(created_design.article, self.article)
        self.assertEqual(created_design.leather_color, Design.COLOR_DARK_BROWN)
        self.assertEqual(created_design.custom_text, 'ALICE 2026')

        expected_redirect = reverse('design_detail', kwargs={'design_id': created_design.id})
        self.assertRedirects(response, expected_redirect)

    def test_design_detail_view_success(self):
        """Test viewing design detail page for own design."""
        self.client.force_login(self.user_a)
        design = Design.objects.create(
            user=self.user_a,
            article=self.article,
            name='Alice Classic Tote',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_RED,
            leather_finish=Design.FINISH_GLOSSY,
            width=Decimal('30.0'),
            height=Decimal('25.0'),
            depth=Decimal('10.0'),
            stitching_color=Design.STITCH_WHITE,
            custom_text='EXCLUSIVE',
            font=Design.FONT_BOLD,
            text_size=28
        )
        url = reverse('design_detail', kwargs={'design_id': design.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'designs/design_detail.html')
        self.assertContains(response, 'Alice Classic Tote')
        self.assertContains(response, 'Classic Leather Wallet')
        self.assertContains(response, 'Red')
        self.assertContains(response, '30.00 cm')
        self.assertContains(response, 'EXCLUSIVE')

    def test_ownership_isolation_prevents_user_b_access(self):
        """Test that User B cannot access User A's design details (returns 404)."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.article,
            name='Alice Private Design',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_BLACK,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_BLACK,
        )
        # Log in as User B
        self.client.force_login(self.user_b)
        url = reverse('design_detail', kwargs={'design_id': design.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

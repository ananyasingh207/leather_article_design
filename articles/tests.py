from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
from .models import Article


class Phase1RoutesTestCase(TestCase):
    """
    Verification tests for Phase 1: Foundation and public views.
    """

    def setUp(self):
        self.client = Client()

    def test_home_page_status_and_content(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'LeatherCraft')
        self.assertContains(response, 'Design Leather Products')
        self.assertContains(response, 'Customize Designs')
        self.assertContains(response, 'Wallets')
        self.assertContains(response, 'Belts')
        self.assertContains(response, 'Handbags')

    def test_about_page_status_and_content(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'about.html')
        self.assertContains(response, 'About LeatherCraft Designer')
        self.assertContains(response, 'The Problem We Solve')

    def test_login_page_status_and_content(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'auth/login.html')
        self.assertContains(response, 'Welcome Back')
        self.assertContains(response, 'Email Address')

    def test_register_page_status_and_content(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertContains(response, 'Create an Account')
        self.assertContains(response, 'Full Name')


class ArticleCatalogTestCase(TestCase):
    """
    Test suite for Phase 3: Leather Article Catalog, Search, Filter, Detail, and Design Placeholder.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='artisan_elena',
            email='elena@craft.com',
            password='TestPassword123!',
            first_name='Elena'
        )

        self.wallet = Article.objects.create(
            name='Classic Leather Wallet',
            category=Article.CATEGORY_WALLETS,
            material='Full Grain Leather',
            base_price=Decimal('500.00'),
            description='A bifold leather wallet with multiple card slots.'
        )

        self.belt = Article.objects.create(
            name='Classic Leather Belt',
            category=Article.CATEGORY_BELTS,
            material='Bridle Leather',
            base_price=Decimal('700.00'),
            description='Heavy-duty dress and utility belt.'
        )

        self.handbag = Article.objects.create(
            name='Everyday Leather Handbag',
            category=Article.CATEGORY_HANDBAGS,
            material='Pull-Up Leather',
            base_price=Decimal('2800.00'),
            description='Spacious tote bag for everyday essentials.'
        )

    def test_article_model_str(self):
        """Test Article string representation."""
        self.assertEqual(str(self.wallet), 'Classic Leather Wallet (Wallets)')

    def test_catalog_access_unauthenticated_redirects(self):
        """Test that unauthenticated visitors are redirected to login."""
        url = reverse('article_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_catalog_access_authenticated(self):
        """Test that authenticated users can view the catalog."""
        self.client.force_login(self.user)
        url = reverse('article_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article_list.html')
        self.assertContains(response, 'Classic Leather Wallet')
        self.assertContains(response, 'Classic Leather Belt')
        self.assertContains(response, 'Everyday Leather Handbag')
        self.assertContains(response, '₹500.00')

    def test_catalog_search_by_query(self):
        """Test searching articles by name or description."""
        self.client.force_login(self.user)
        url = reverse('article_list')
        response = self.client.get(url, {'q': 'wallet'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classic Leather Wallet')
        self.assertNotContains(response, 'Classic Leather Belt')
        self.assertNotContains(response, 'Everyday Leather Handbag')

    def test_catalog_filter_by_category(self):
        """Test filtering articles by category."""
        self.client.force_login(self.user)
        url = reverse('article_list')
        response = self.client.get(url, {'category': 'Belts'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classic Leather Belt')
        self.assertNotContains(response, 'Classic Leather Wallet')
        self.assertNotContains(response, 'Everyday Leather Handbag')

    def test_catalog_combined_search_and_filter(self):
        """Test search query combined with category filter."""
        self.client.force_login(self.user)
        url = reverse('article_list')
        response = self.client.get(url, {'q': 'leather', 'category': 'Handbags'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Everyday Leather Handbag')
        self.assertNotContains(response, 'Classic Leather Wallet')
        self.assertNotContains(response, 'Classic Leather Belt')

    def test_catalog_empty_search_results(self):
        """Test empty search result displays Clear Filters option."""
        self.client.force_login(self.user)
        url = reverse('article_list')
        response = self.client.get(url, {'q': 'NonExistentProductXYZ'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Articles Found')
        self.assertContains(response, 'Clear Filters')

    def test_article_detail_view_valid_id(self):
        """Test viewing article detail for existing article."""
        self.client.force_login(self.user)
        url = reverse('article_detail', kwargs={'article_id': self.wallet.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article_detail.html')
        self.assertContains(response, 'Classic Leather Wallet')
        self.assertContains(response, 'Full Grain Leather')
        self.assertContains(response, '₹500.00')
        self.assertContains(response, 'Design This Article')

    def test_article_detail_view_invalid_id_returns_404(self):
        """Test viewing non-existent article returns 404."""
        self.client.force_login(self.user)
        url = reverse('article_detail', kwargs={'article_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_design_article_placeholder_view_valid_id(self):
        """Test design placeholder view for an article."""
        self.client.force_login(self.user)
        url = reverse('design_article', kwargs={'article_id': self.wallet.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/design_placeholder.html')
        self.assertContains(response, 'Design Studio')
        self.assertContains(response, 'Classic Leather Wallet')
        self.assertContains(response, 'Phase 4')

    def test_design_article_placeholder_view_invalid_id_returns_404(self):
        """Test design placeholder for non-existent article returns 404."""
        self.client.force_login(self.user)
        url = reverse('design_article', kwargs={'article_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_management_command_populate_sample_articles(self):
        """Test running management command populates all 7 categories without error."""
        call_command('populate_sample_articles')
        self.assertEqual(Article.objects.filter(category=Article.CATEGORY_WALLETS).exists(), True)
        self.assertEqual(Article.objects.filter(category=Article.CATEGORY_BELTS).exists(), True)
        self.assertEqual(Article.objects.filter(category=Article.CATEGORY_HANDBAGS).exists(), True)
        self.assertEqual(Article.objects.filter(category=Article.CATEGORY_CARD_HOLDERS).exists(), True)
        self.assertEqual(Article.objects.filter(category=Article.CATEGORY_KEYCHAINS).exists(), True)
        self.assertEqual(Article.objects.filter(category=Article.CATEGORY_POUCHES).exists(), True)
        self.assertEqual(Article.objects.filter(category=Article.CATEGORY_LEATHER_COVERS).exists(), True)




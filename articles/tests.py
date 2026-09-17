from django.test import TestCase, Client
from django.urls import reverse


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
        self.assertContains(response, 'Phase 1 Preview')

    def test_register_page_status_and_content(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertContains(response, 'Create an Account')
        self.assertContains(response, 'Full Name')


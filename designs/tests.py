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

    def test_design_studio_interactive_controls_present(self):
        """Test Phase 5 interactive controls, sliders, side switcher, and asset links in Design Studio."""
        self.client.force_login(self.user_a)
        url = reverse('design_create', kwargs={'article_id': self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check interactive sliders and buttons
        self.assertContains(response, 'id="sliderPosX"')
        self.assertContains(response, 'id="sliderPosY"')
        self.assertContains(response, 'id="sliderRotation"')
        self.assertContains(response, 'id="btnResetPreview"')
        self.assertContains(response, 'id="tabViewFront"')
        self.assertContains(response, 'id="tabViewBack"')
        self.assertContains(response, 'id="tabViewSide"')

        # Check canvas and category shape
        self.assertContains(response, 'id="studioCanvasStage"')
        self.assertContains(response, 'shape-wallets')
        self.assertContains(response, 'design_studio.js')
        self.assertContains(response, 'design_studio.css')

    def test_design_studio_multiple_article_category_shapes(self):
        """Test that different article categories render their respective category shape classes."""
        self.client.force_login(self.user_a)

        categories_to_test = [
            (Article.CATEGORY_BELTS, 'shape-belts'),
            (Article.CATEGORY_HANDBAGS, 'shape-handbags'),
            (Article.CATEGORY_CARD_HOLDERS, 'shape-card-holders'),
            (Article.CATEGORY_KEYCHAINS, 'shape-keychains'),
            (Article.CATEGORY_POUCHES, 'shape-pouches'),
            (Article.CATEGORY_LEATHER_COVERS, 'shape-leather-covers'),
        ]

        for cat, expected_shape_class in categories_to_test:
            art = Article.objects.create(
                name=f"Sample {cat}",
                category=cat,
                material="Top Grain Leather",
                base_price=Decimal("900.00"),
                description=f"Sample product for {cat}"
            )
            url = reverse('design_create', kwargs={'article_id': art.id})
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, expected_shape_class)


class Phase6DesignManagementTestCase(TestCase):
    """
    Test suite for Phase 6: Save & Manage Designs.
    Verifies My Designs list, search & filters, edit, duplicate, delete, dashboard integration, and strict security isolation.
    """

    def setUp(self):
        self.client = Client()
        self.user_a = User.objects.create_user(
            username='artisan_alice',
            email='alice@craft.com',
            password='AlicePassword123!'
        )
        self.user_b = User.objects.create_user(
            username='artisan_bob',
            email='bob@craft.com',
            password='BobPassword123!'
        )
        self.wallet_article = Article.objects.create(
            name='Heritage Leather Wallet',
            category=Article.CATEGORY_WALLETS,
            material='Full Grain Leather',
            base_price=Decimal('550.00'),
            description='Handmade bifold wallet.'
        )
        self.belt_article = Article.objects.create(
            name='Classic Leather Belt',
            category=Article.CATEGORY_BELTS,
            material='Top Grain Leather',
            base_price=Decimal('750.00'),
            description='Handcrafted full grain belt.'
        )

    def test_my_designs_page_lists_only_current_user_designs(self):
        """Test 1: My Designs lists only the current user's designs with full card details."""
        design_a = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Alice Custom Bifold',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_BROWN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_BROWN,
            custom_text='ALICE',
            font=Design.FONT_CLASSIC,
            text_size=18,
            position_x=50,
            position_y=50,
            rotation=0,
            selected_side='front',
        )
        design_b = Design.objects.create(
            user=self.user_b,
            article=self.belt_article,
            name='Bob Private Belt',
            leather_type=Design.LEATHER_TYPE_TOP_GRAIN,
            leather_color=Design.COLOR_BLACK,
            leather_finish=Design.FINISH_SMOOTH,
            width=Decimal('100.0'),
            height=Decimal('3.5'),
            depth=Decimal('0.4'),
            stitching_color=Design.STITCH_BLACK,
        )

        self.client.force_login(self.user_a)
        response = self.client.get(reverse('design_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'designs/design_list.html')
        # User A's design is displayed
        self.assertContains(response, 'Alice Custom Bifold')
        self.assertContains(response, 'Heritage Leather Wallet')
        self.assertContains(response, 'Full Grain Leather')
        self.assertContains(response, 'Brown')
        self.assertContains(response, '11.50 × 9.00 × 2.00 cm')
        # View, Edit, Duplicate, Delete actions are present
        self.assertContains(response, reverse('design_detail', kwargs={'design_id': design_a.id}))
        self.assertContains(response, reverse('design_edit', kwargs={'design_id': design_a.id}))
        self.assertContains(response, reverse('design_duplicate', kwargs={'design_id': design_a.id}))
        self.assertContains(response, reverse('design_delete', kwargs={'design_id': design_a.id}))
        # User B's design is NOT displayed
        self.assertNotContains(response, 'Bob Private Belt')

    def test_my_designs_empty_state(self):
        """Test 2: Empty state works with Create Your First Design button."""
        self.client.force_login(self.user_b)
        response = self.client.get(reverse('design_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Custom Designs Yet')
        self.assertContains(response, 'Create Your First Design')
        self.assertContains(response, reverse('article_list'))

    def test_my_designs_search_and_category_filtering_work_together(self):
        """Test 3: Search and category filtering use GET parameters and work together."""
        Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Vintage Tan Wallet',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_TAN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('11.0'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_TAN,
        )
        Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Modern Black Pocket',
            leather_type=Design.LEATHER_TYPE_TOP_GRAIN,
            leather_color=Design.COLOR_BLACK,
            leather_finish=Design.FINISH_SMOOTH,
            width=Decimal('10.5'),
            height=Decimal('8.5'),
            depth=Decimal('1.8'),
            stitching_color=Design.STITCH_BLACK,
        )
        Design.objects.create(
            user=self.user_a,
            article=self.belt_article,
            name='Vintage Tan Belt',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_TAN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('110.0'),
            height=Decimal('3.8'),
            depth=Decimal('0.4'),
            stitching_color=Design.STITCH_TAN,
        )

        self.client.force_login(self.user_a)

        # 1. Search only: 'Vintage' -> matches Wallet & Belt
        url = reverse('design_list') + '?q=Vintage'
        resp = self.client.get(url)
        self.assertContains(resp, 'Vintage Tan Wallet')
        self.assertContains(resp, 'Vintage Tan Belt')
        self.assertNotContains(resp, 'Modern Black Pocket')

        # 2. Filter only: 'Wallets' category -> matches both Wallets
        url = reverse('design_list') + f'?category={Article.CATEGORY_WALLETS}'
        resp = self.client.get(url)
        self.assertContains(resp, 'Vintage Tan Wallet')
        self.assertContains(resp, 'Modern Black Pocket')
        self.assertNotContains(resp, 'Vintage Tan Belt')

        # 3. Combined Search + Category Filter: 'Vintage' + 'Wallets' -> matches ONLY Vintage Tan Wallet
        url = reverse('design_list') + f'?q=Vintage&category={Article.CATEGORY_WALLETS}'
        resp = self.client.get(url)
        self.assertContains(resp, 'Vintage Tan Wallet')
        self.assertNotContains(resp, 'Vintage Tan Belt')
        self.assertNotContains(resp, 'Modern Black Pocket')

        # 4. Search by article name
        url = reverse('design_list') + '?q=Leather+Belt'
        resp = self.client.get(url)
        self.assertContains(resp, 'Vintage Tan Belt')
        self.assertNotContains(resp, 'Modern Black Pocket')

    def test_saved_values_load_correctly_into_editor(self):
        """Test 4: Saved values load into the Design Studio form and preview on edit route."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Custom Initialized Wallet',
            leather_type=Design.LEATHER_TYPE_TOP_GRAIN,
            leather_color=Design.COLOR_DARK_BROWN,
            leather_finish=Design.FINISH_TEXTURED,
            width=Decimal('12.5'),
            height=Decimal('9.5'),
            depth=Decimal('2.5'),
            stitching_color=Design.STITCH_RED,
            custom_text='HERITAGE',
            font=Design.FONT_ELEGANT,
            text_size=24,
            position_x=72,
            position_y=38,
            rotation=15,
            selected_side='back',
        )

        self.client.force_login(self.user_a)
        url = reverse('design_edit', kwargs={'design_id': design.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'designs/design_form.html')
        # Form contains saved values
        self.assertContains(response, 'value="Custom Initialized Wallet"')
        self.assertContains(response, 'value="12.50"')
        self.assertContains(response, 'value="9.50"')
        self.assertContains(response, 'value="2.50"')
        self.assertContains(response, 'value="HERITAGE"')
        self.assertContains(response, 'value="72"')
        self.assertContains(response, 'value="38"')
        self.assertContains(response, 'value="15"')
        self.assertContains(response, 'value="back"')
        # Cancel button points back to design detail
        self.assertContains(response, reverse('design_detail', kwargs={'design_id': design.id}))

    def test_editing_updates_same_record_and_auto_updates_timestamp(self):
        """Test 5: Submitting valid changes updates the existing record and updates updated_at."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Original Wallet Name',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_BROWN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_BROWN,
            custom_text='OLD',
            position_x=50,
            position_y=50,
            rotation=0,
            selected_side='front',
        )
        original_pk = design.pk
        original_updated_at = design.updated_at

        self.client.force_login(self.user_a)
        edit_url = reverse('design_edit', kwargs={'design_id': design.id})
        post_data = {
            'name': 'Updated Wallet Name',
            'leather_type': Design.LEATHER_TYPE_SUEDE,
            'leather_color': Design.COLOR_RED,
            'leather_finish': Design.FINISH_GLOSSY,
            'width': '13.0',
            'height': '10.0',
            'depth': '2.5',
            'stitching_color': Design.STITCH_WHITE,
            'custom_text': 'NEW-TEXT',
            'font': Design.FONT_BOLD,
            'text_size': 28,
            'position_x': 65,
            'position_y': 45,
            'rotation': -10,
            'selected_side': 'side',
        }

        response = self.client.post(edit_url, post_data)
        # Record count must still be 1 (no new record created)
        self.assertEqual(Design.objects.count(), 1)
        # Redirect to design detail page
        self.assertRedirects(response, reverse('design_detail', kwargs={'design_id': original_pk}))

        # Verify updated values in database
        design.refresh_from_db()
        self.assertEqual(design.pk, original_pk)
        self.assertEqual(design.name, 'Updated Wallet Name')
        self.assertEqual(design.leather_type, Design.LEATHER_TYPE_SUEDE)
        self.assertEqual(design.leather_color, Design.COLOR_RED)
        self.assertEqual(design.custom_text, 'NEW-TEXT')
        self.assertEqual(design.position_x, 65)
        self.assertEqual(design.position_y, 45)
        self.assertEqual(design.rotation, -10)
        self.assertEqual(design.selected_side, 'side')
        self.assertGreaterEqual(design.updated_at, original_updated_at)

    def test_preview_settings_persist_after_editing_and_reopening(self):
        """Test 6: Preview settings persist after editing and reopening the design detail and edit pages."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Persistence Test Wallet',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_BLUE,
            leather_finish=Design.FINISH_GLOSSY,
            width=Decimal('12.0'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_RED,
            custom_text='PERSIST',
            font=Design.FONT_BOLD,
            text_size=20,
            position_x=80,
            position_y=25,
            rotation=12,
            selected_side='back',
        )

        self.client.force_login(self.user_a)

        # Check detail page displays stored position and rotation
        detail_url = reverse('design_detail', kwargs={'design_id': design.id})
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'left: 80%')
        self.assertContains(resp, 'top: 25%')
        self.assertContains(resp, 'rotate(12deg)')
        self.assertContains(resp, 'Back View')

        # Check edit page reopens with stored values
        edit_url = reverse('design_edit', kwargs={'design_id': design.id})
        resp_edit = self.client.get(edit_url)
        self.assertEqual(resp_edit.status_code, 200)
        self.assertContains(resp_edit, 'value="80"')
        self.assertContains(resp_edit, 'value="25"')
        self.assertContains(resp_edit, 'value="12"')
        self.assertContains(resp_edit, 'value="back"')

    def test_canceling_deletion_preserves_the_design(self):
        """Test 7: Canceling deletion leaves the design unchanged in database."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Preserve Me Wallet',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_BROWN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_BROWN,
        )

        self.client.force_login(self.user_a)
        delete_url = reverse('design_delete', kwargs={'design_id': design.id})
        # GET request only displays confirmation page
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'designs/design_confirm_delete.html')
        self.assertContains(response, 'Preserve Me Wallet')
        # Design must NOT be deleted by a GET request
        self.assertTrue(Design.objects.filter(pk=design.id).exists())

    def test_confirming_deletion_removes_the_design(self):
        """Test 8: Confirming deletion via POST removes the design and redirects to My Designs."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Delete Me Wallet',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_BROWN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_BROWN,
        )

        self.client.force_login(self.user_a)
        delete_url = reverse('design_delete', kwargs={'design_id': design.id})
        # POST performs deletion
        response = self.client.post(delete_url)
        self.assertFalse(Design.objects.filter(pk=design.id).exists())
        self.assertRedirects(response, reverse('design_list'))

    def test_duplicating_creates_separate_copy_and_preserves_original(self):
        """Test 9: Duplicating creates a separate record with distinct name and preserves the original."""
        original = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Original Classic Wallet',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_TAN,
            leather_finish=Design.FINISH_SMOOTH,
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_TAN,
            custom_text='ORIGINAL',
            font=Design.FONT_CLASSIC,
            text_size=18,
            position_x=40,
            position_y=60,
            rotation=5,
            selected_side='front',
        )

        self.client.force_login(self.user_a)
        dup_url = reverse('design_duplicate', kwargs={'design_id': original.id})
        response = self.client.post(dup_url)

        # Count increased to 2
        self.assertEqual(Design.objects.count(), 2)

        # Original is completely preserved
        original.refresh_from_db()
        self.assertEqual(original.name, 'Original Classic Wallet')

        # New copy exists
        new_design = Design.objects.exclude(pk=original.pk).first()
        self.assertEqual(new_design.name, 'Original Classic Wallet (Copy)')
        self.assertEqual(new_design.user, self.user_a)
        self.assertEqual(new_design.article, original.article)
        self.assertEqual(new_design.width, original.width)
        self.assertEqual(new_design.custom_text, original.custom_text)
        self.assertEqual(new_design.position_x, 40)
        self.assertEqual(new_design.position_y, 60)
        self.assertEqual(new_design.rotation, 5)

        # Redirects to new design detail
        self.assertRedirects(response, reverse('design_detail', kwargs={'design_id': new_design.id}))

    def test_dashboard_count_reflects_the_database(self):
        """Test 10: Dashboard count dynamically reflects the logged-in user's designs."""
        self.client.force_login(self.user_a)
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.context['my_designs_count'], 0)

        # Create 2 designs
        Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Wallet 1',
            width=Decimal('10.0'),
            height=Decimal('8.0'),
            depth=Decimal('1.5'),
        )
        Design.objects.create(
            user=self.user_a,
            article=self.belt_article,
            name='Belt 1',
            width=Decimal('100.0'),
            height=Decimal('3.5'),
            depth=Decimal('0.4'),
        )

        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.context['my_designs_count'], 2)
        self.assertContains(resp, 'My Designs')
        self.assertContains(resp, reverse('design_list'))

    def test_security_isolation_prevents_unauthorized_access_or_modification(self):
        """Test 11: Another user cannot access or modify a design through manipulated URLs or POST requests."""
        alice_design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Alice Confidential Design',
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
        )

        # Log in as Bob
        self.client.force_login(self.user_b)

        # Bob attempts GET detail -> 404
        resp = self.client.get(reverse('design_detail', kwargs={'design_id': alice_design.id}))
        self.assertEqual(resp.status_code, 404)

        # Bob attempts GET edit -> 404
        resp = self.client.get(reverse('design_edit', kwargs={'design_id': alice_design.id}))
        self.assertEqual(resp.status_code, 404)

        # Bob attempts POST edit -> 404
        resp = self.client.post(reverse('design_edit', kwargs={'design_id': alice_design.id}), {'name': 'Hacked'})
        self.assertEqual(resp.status_code, 404)
        alice_design.refresh_from_db()
        self.assertEqual(alice_design.name, 'Alice Confidential Design')

        # Bob attempts POST duplicate -> 404
        resp = self.client.post(reverse('design_duplicate', kwargs={'design_id': alice_design.id}))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Design.objects.filter(user=self.user_b).count(), 0)

        # Bob attempts GET delete -> 404
        resp = self.client.get(reverse('design_delete', kwargs={'design_id': alice_design.id}))
        self.assertEqual(resp.status_code, 404)

        # Bob attempts POST delete -> 404
        resp = self.client.post(reverse('design_delete', kwargs={'design_id': alice_design.id}))
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Design.objects.filter(pk=alice_design.id).exists())

    def test_unauthenticated_requests_redirect_to_login(self):
        """Test 12: Unauthenticated requests to all design management routes redirect to login."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Test Protected Design',
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
        )

        routes = [
            reverse('design_list'),
            reverse('design_detail', kwargs={'design_id': design.id}),
            reverse('design_edit', kwargs={'design_id': design.id}),
            reverse('design_delete', kwargs={'design_id': design.id}),
            reverse('design_duplicate', kwargs={'design_id': design.id}),
        ]

        for route in routes:
            resp = self.client.get(route)
            self.assertEqual(resp.status_code, 302)
            self.assertTrue(resp.url.startswith('/login/'))


class CostEstimationTests(TestCase):
    """
    Phase 7: Test suite for Simple Cost Estimation calculation service,
    model properties, Design Studio live integration, and saved-design detail page.
    """

    def setUp(self):
        self.user_a = User.objects.create_user(username='artisan_a', password='Password123!')
        self.user_b = User.objects.create_user(username='artisan_b', password='Password123!')

        self.wallet_article = Article.objects.create(
            name='Bifold Wallet',
            category=Article.CATEGORY_WALLETS,
            material='Full Grain Leather',
            base_price=Decimal('1200.00'),
        )

        self.belt_article = Article.objects.create(
            name='Classic Belt',
            category=Article.CATEGORY_BELTS,
            material='Top Grain Leather',
            base_price=Decimal('1850.50'),
        )

    def test_pricing_service_base_price_only_with_defaults(self):
        """Test 1: Starting price is base_price, default black stitching has ₹0 surcharge, no custom text has ₹0 surcharge."""
        from designs.services import calculate_design_cost

        estimate = calculate_design_cost(
            base_price=self.wallet_article.base_price,
            leather_type=Design.LEATHER_TYPE_GENUINE,
            stitching_color='Black',
            custom_text='',
        )

        self.assertEqual(estimate['base_price'], Decimal('1200.00'))
        self.assertEqual(estimate['leather_surcharge'], Decimal('50.00'))
        self.assertEqual(estimate['stitching_surcharge'], Decimal('0.00'))
        self.assertEqual(estimate['custom_text_surcharge'], Decimal('0.00'))
        # 1200 + 50 + 0 + 0 = 1250.00
        self.assertEqual(estimate['total_estimate'], Decimal('1250.00'))

    def test_pricing_service_all_leather_types(self):
        """Test 2: Verify exact surcharges for each leather type: Full Grain (150), Top Grain (100), Genuine (50), Suede (100)."""
        from designs.services import calculate_design_cost

        cases = [
            (Design.LEATHER_TYPE_FULL_GRAIN, Decimal('150.00')),
            (Design.LEATHER_TYPE_TOP_GRAIN, Decimal('100.00')),
            (Design.LEATHER_TYPE_GENUINE, Decimal('50.00')),
            (Design.LEATHER_TYPE_SUEDE, Decimal('100.00')),
            ('Unknown Leather Type', Decimal('0.00')),
        ]

        for leather_type, expected_surcharge in cases:
            with self.subTest(leather_type=leather_type):
                cost = calculate_design_cost(
                    base_price=Decimal('1000.00'),
                    leather_type=leather_type,
                    stitching_color='Black',
                    custom_text='',
                )
                self.assertEqual(cost['leather_surcharge'], expected_surcharge)
                self.assertEqual(cost['total_estimate'], Decimal('1000.00') + expected_surcharge)

    def test_pricing_service_stitching_surcharges(self):
        """Test 3: Black stitching is ₹0; non-black stitching is ₹50."""
        from designs.services import calculate_design_cost

        # Default black
        cost_black = calculate_design_cost(
            base_price=Decimal('1000.00'),
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            stitching_color='Black',
        )
        self.assertEqual(cost_black['stitching_surcharge'], Decimal('0.00'))

        # Case-insensitive black
        cost_black_lower = calculate_design_cost(
            base_price=Decimal('1000.00'),
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            stitching_color=' black ',
        )
        self.assertEqual(cost_black_lower['stitching_surcharge'], Decimal('0.00'))

        # Non-black stitching colors: Brown, White, Red, Tan
        for color in ['Brown', 'White', 'Red', 'Tan', 'Gold']:
            with self.subTest(color=color):
                cost_color = calculate_design_cost(
                    base_price=Decimal('1000.00'),
                    leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
                    stitching_color=color,
                )
                self.assertEqual(cost_color['stitching_surcharge'], Decimal('50.00'))

    def test_pricing_service_custom_text_surcharges(self):
        """Test 4: Empty or whitespace custom text is ₹0; non-empty custom text is ₹25."""
        from designs.services import calculate_design_cost

        # Empty / None / Whitespace
        for empty_val in ['', '   ', None]:
            with self.subTest(empty_val=empty_val):
                cost = calculate_design_cost(
                    base_price=Decimal('1000.00'),
                    leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
                    stitching_color='Black',
                    custom_text=empty_val,
                )
                self.assertEqual(cost['custom_text_surcharge'], Decimal('0.00'))

        # Non-empty custom text
        for text in ['J.D.', 'LEATHER', '  MONOGRAM  ']:
            with self.subTest(text=text):
                cost = calculate_design_cost(
                    base_price=Decimal('1000.00'),
                    leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
                    stitching_color='Black',
                    custom_text=text,
                )
                self.assertEqual(cost['custom_text_surcharge'], Decimal('25.00'))

    def test_combined_authoritative_calculation_with_decimal_arithmetic(self):
        """Test 5: Verify combined calculation accuracy: 1850.50 + 100 + 50 + 25 = 2025.50."""
        from designs.services import calculate_design_cost

        cost = calculate_design_cost(
            base_price=self.belt_article.base_price,  # 1850.50
            leather_type=Design.LEATHER_TYPE_TOP_GRAIN,  # +100.00
            stitching_color=Design.STITCH_RED,  # +50.00
            custom_text='CUSTOM BELT',  # +25.00
        )

        self.assertEqual(cost['base_price'], Decimal('1850.50'))
        self.assertEqual(cost['leather_surcharge'], Decimal('100.00'))
        self.assertEqual(cost['stitching_surcharge'], Decimal('50.00'))
        self.assertEqual(cost['custom_text_surcharge'], Decimal('25.00'))
        self.assertEqual(cost['total_estimate'], Decimal('2025.50'))

    def test_design_model_dynamic_cost_properties(self):
        """Test 6: Design model properties cost_breakdown and estimated_total dynamically compute cost."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,  # base_price 1200.00
            name='Dynamic Cost Wallet',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,  # +150.00
            stitching_color=Design.STITCH_BROWN,  # +50.00
            custom_text='INITIALS',  # +25.00
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
        )

        breakdown = design.cost_breakdown
        self.assertEqual(breakdown['base_price'], Decimal('1200.00'))
        self.assertEqual(breakdown['leather_surcharge'], Decimal('150.00'))
        self.assertEqual(breakdown['stitching_surcharge'], Decimal('50.00'))
        self.assertEqual(breakdown['custom_text_surcharge'], Decimal('25.00'))
        self.assertEqual(breakdown['total_estimate'], Decimal('1425.00'))
        self.assertEqual(design.estimated_total, Decimal('1425.00'))

    def test_design_studio_form_renders_cost_breakdown_elements(self):
        """Test 7: Design Studio template renders cost estimator panel, base price attribute, and disclaimer note."""
        self.client.force_login(self.user_a)
        url = reverse('design_create', kwargs={'article_id': self.wallet_article.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'designs/design_form.html')
        # Check context
        self.assertIn('cost_estimate', response.context)
        # Check HTML markup for Phase 7
        self.assertContains(response, 'id="costEstimatorPanel"')
        self.assertContains(response, f'data-base-price="{self.wallet_article.base_price}"')
        self.assertContains(response, 'id="costBasePrice"')
        self.assertContains(response, 'id="costLeatherSurcharge"')
        self.assertContains(response, 'id="costStitchingSurcharge"')
        self.assertContains(response, 'id="costCustomTextSurcharge"')
        self.assertContains(response, 'id="costTotalAmount"')
        self.assertContains(response, 'id="readoutEstimatedCost"')
        self.assertContains(response, '* Note: Estimated price for reference only')
        self.assertContains(response, '₹')

    def test_saved_design_detail_displays_cost_breakdown_and_estimate(self):
        """Test 8: Saved design detail page displays accurate cost breakdown for saved configuration."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,  # 1200.00
            name='Detail Test Wallet',
            leather_type=Design.LEATHER_TYPE_SUEDE,  # +100.00
            stitching_color=Design.STITCH_BLACK,  # +0.00
            custom_text='',  # +0.00
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
        )

        self.client.force_login(self.user_a)
        url = reverse('design_detail', kwargs={'design_id': design.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'designs/design_detail.html')
        self.assertIn('cost_estimate', response.context)
        self.assertEqual(response.context['cost_estimate']['total_estimate'], Decimal('1300.00'))

        # Check HTML breakdown panel
        self.assertContains(response, 'Cost Estimation Breakdown')
        self.assertContains(response, 'id="detailCostBasePrice"')
        self.assertContains(response, '₹1200.00')
        self.assertContains(response, 'id="detailCostLeather"')
        self.assertContains(response, '+₹100.00')
        self.assertContains(response, 'id="detailCostTotal"')
        self.assertContains(response, '₹1300.00')
        self.assertContains(response, '* Note: Estimated price for reference only')

    def test_my_designs_list_displays_estimated_total(self):
        """Test 9: My Designs list page displays estimated total on design cards."""
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='My List Wallet',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            stitching_color=Design.STITCH_BROWN,
            custom_text='CUSTOM',
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
        )

        self.client.force_login(self.user_a)
        response = self.client.get(reverse('design_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Est. Cost:')
        self.assertContains(response, f'₹{design.estimated_total}')

    def test_cost_calculation_is_authoritative_on_backend(self):
        """Test 10: Backend computes authoritative cost on save; client manipulation does not bypass backend."""
        self.client.force_login(self.user_a)
        post_data = {
            'name': 'Client Spoof Test',
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,  # +150
            'leather_color': Design.COLOR_BROWN,
            'leather_finish': Design.FINISH_MATTE,
            'width': '12.0',
            'height': '9.0',
            'depth': '2.0',
            'stitching_color': Design.STITCH_RED,  # +50
            'custom_text': 'REAL TEXT',  # +25
            'font': Design.FONT_CLASSIC,
            'text_size': 18,
            'position_x': 50,
            'position_y': 50,
            'rotation': 0,
            'selected_side': 'front',
            'fake_client_total': '0.00',  # Attempted spoof
        }

        url = reverse('design_create', kwargs={'article_id': self.wallet_article.id})
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        created_design = Design.objects.get(name='Client Spoof Test')
        # Total must strictly be: 1200.00 + 150.00 + 50.00 + 25.00 = 1425.00
        self.assertEqual(created_design.estimated_total, Decimal('1425.00'))


class LogoCustomizationTests(TestCase):
    """
    Phase 8: Comprehensive test suite for Simple Logo Customization:
    - Upload PNG logo
    - Upload JPEG logo
    - Persist logo across reopen / edit / detail
    - Replace existing logo
    - Remove logo
    - Reject invalid file formats and fake images
    - User ownership and isolation checks
    - Duplicate design preserves logo
    """

    def setUp(self):
        self.user_a = User.objects.create_user(username='artisan_logo_a', password='Password123!')
        self.user_b = User.objects.create_user(username='artisan_logo_b', password='Password123!')

        self.wallet_article = Article.objects.create(
            name='Luxury Bi-Fold Wallet',
            category=Article.CATEGORY_WALLETS,
            material='Full Grain Leather',
            base_price=Decimal('1500.00'),
        )

    def _create_test_image(self, format='PNG', filename='logo.png', size=(80, 80), color=(180, 100, 50)):
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        file_obj = BytesIO()
        mode = 'RGBA' if format == 'PNG' else 'RGB'
        img = Image.new(mode, size, color=color)
        img.save(file_obj, format=format)
        file_obj.seek(0)
        content_type = 'image/png' if format == 'PNG' else 'image/jpeg'
        return SimpleUploadedFile(filename, file_obj.read(), content_type=content_type)

    def test_upload_png_logo_success(self):
        """Test 1: Uploading a valid PNG logo attaches the image to the design."""
        self.client.force_login(self.user_a)
        png_file = self._create_test_image(format='PNG', filename='brand_crest.png')

        post_data = {
            'name': 'Branded PNG Wallet',
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,
            'leather_color': Design.COLOR_BROWN,
            'leather_finish': Design.FINISH_MATTE,
            'width': '11.5',
            'height': '9.0',
            'depth': '2.0',
            'stitching_color': Design.STITCH_BROWN,
            'custom_text': 'ROYAL',
            'font': Design.FONT_CLASSIC,
            'text_size': 18,
            'position_x': 50,
            'position_y': 50,
            'rotation': 0,
            'selected_side': 'front',
            'logo': png_file,
        }

        url = reverse('design_create', kwargs={'article_id': self.wallet_article.id})
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        design = Design.objects.get(name='Branded PNG Wallet')
        self.assertTrue(bool(design.logo))
        self.assertTrue(design.logo.name.endswith('.png'))

        # Detail page renders the logo
        detail_url = reverse('design_detail', kwargs={'design_id': design.id})
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, design.logo.url)
        self.assertContains(resp, 'id="detailLiveLogoContainer"')

    def test_upload_jpeg_logo_success(self):
        """Test 2: Uploading a valid JPEG logo attaches the image to the design."""
        self.client.force_login(self.user_a)
        jpeg_file = self._create_test_image(format='JPEG', filename='monogram.jpg')

        post_data = {
            'name': 'Branded JPEG Wallet',
            'leather_type': Design.LEATHER_TYPE_TOP_GRAIN,
            'leather_color': Design.COLOR_TAN,
            'leather_finish': Design.FINISH_SMOOTH,
            'width': '11.5',
            'height': '9.0',
            'depth': '2.0',
            'stitching_color': Design.STITCH_BLACK,
            'custom_text': '',
            'font': Design.FONT_CLASSIC,
            'text_size': 18,
            'position_x': 50,
            'position_y': 50,
            'rotation': 0,
            'selected_side': 'front',
            'logo': jpeg_file,
        }

        url = reverse('design_create', kwargs={'article_id': self.wallet_article.id})
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        design = Design.objects.get(name='Branded JPEG Wallet')
        self.assertTrue(bool(design.logo))
        self.assertTrue(design.logo.name.endswith('.jpg') or design.logo.name.endswith('.jpeg'))

    def test_saved_design_reopen_persists_logo_in_editor(self):
        """Test 3: Reopening a saved design in edit mode displays the existing logo card and removal option."""
        png_file = self._create_test_image(format='PNG', filename='saved_logo.png')
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Persistent Logo Wallet',
            leather_type=Design.LEATHER_TYPE_FULL_GRAIN,
            leather_color=Design.COLOR_BROWN,
            leather_finish=Design.FINISH_MATTE,
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            stitching_color=Design.STITCH_BROWN,
            logo=png_file,
        )

        self.client.force_login(self.user_a)
        edit_url = reverse('design_edit', kwargs={'design_id': design.id})
        response = self.client.get(edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="currentLogoCard"')
        self.assertContains(response, design.logo.url)
        self.assertContains(response, 'id="id_clear_logo"')
        self.assertContains(response, 'Saved Logo Attached')

    def test_replace_existing_logo(self):
        """Test 4: Uploading a new logo in edit mode replaces the existing logo."""
        old_file = self._create_test_image(format='PNG', filename='old_logo.png')
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Replace Logo Wallet',
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            logo=old_file,
        )
        old_logo_name = design.logo.name

        self.client.force_login(self.user_a)
        new_file = self._create_test_image(format='JPEG', filename='new_logo.jpg')

        post_data = {
            'name': 'Replace Logo Wallet',
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,
            'leather_color': Design.COLOR_BROWN,
            'leather_finish': Design.FINISH_MATTE,
            'width': '11.5',
            'height': '9.0',
            'depth': '2.0',
            'stitching_color': Design.STITCH_BROWN,
            'custom_text': '',
            'font': Design.FONT_CLASSIC,
            'text_size': 18,
            'position_x': 50,
            'position_y': 50,
            'rotation': 0,
            'selected_side': 'front',
            'logo': new_file,
        }

        edit_url = reverse('design_edit', kwargs={'design_id': design.id})
        response = self.client.post(edit_url, post_data)
        self.assertEqual(response.status_code, 302)

        design.refresh_from_db()
        self.assertTrue(bool(design.logo))
        self.assertNotEqual(design.logo.name, old_logo_name)
        self.assertTrue(design.logo.name.endswith('.jpg') or design.logo.name.endswith('.jpeg'))

    def test_remove_existing_logo(self):
        """Test 5: Checking clear_logo removes the existing logo and leaves the design intact."""
        logo_file = self._create_test_image(format='PNG', filename='remove_me.png')
        design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Remove Logo Wallet',
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            logo=logo_file,
        )
        self.assertTrue(bool(design.logo))

        self.client.force_login(self.user_a)
        post_data = {
            'name': 'Remove Logo Wallet',
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,
            'leather_color': Design.COLOR_BROWN,
            'leather_finish': Design.FINISH_MATTE,
            'width': '11.5',
            'height': '9.0',
            'depth': '2.0',
            'stitching_color': Design.STITCH_BROWN,
            'custom_text': '',
            'font': Design.FONT_CLASSIC,
            'text_size': 18,
            'position_x': 50,
            'position_y': 50,
            'rotation': 0,
            'selected_side': 'front',
            'clear_logo': 'on',
        }

        edit_url = reverse('design_edit', kwargs={'design_id': design.id})
        response = self.client.post(edit_url, post_data)
        self.assertEqual(response.status_code, 302)

        design.refresh_from_db()
        self.assertFalse(bool(design.logo))

    def test_reject_unsupported_image_format(self):
        """Test 6: Valid images that are not PNG or JPEG (such as GIF) are rejected by format validator."""
        self.client.force_login(self.user_a)
        gif_file = self._create_test_image(format='GIF', filename='animated_logo.gif')

        post_data = {
            'name': 'GIF Logo Wallet',
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,
            'leather_color': Design.COLOR_BROWN,
            'leather_finish': Design.FINISH_MATTE,
            'width': '11.5',
            'height': '9.0',
            'depth': '2.0',
            'stitching_color': Design.STITCH_BROWN,
            'logo': gif_file,
        }

        url = reverse('design_create', kwargs={'article_id': self.wallet_article.id})
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'logo', 'Unsupported file format. Please upload a PNG or JPEG image.')
        self.assertEqual(Design.objects.filter(name='GIF Logo Wallet').count(), 0)

    def test_reject_fake_corrupt_image_content(self):
        """Test 7: A non-image file renamed with a .png extension is rejected safely by image verification."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_login(self.user_a)
        fake_png = SimpleUploadedFile('malicious.png', b'NOT AN ACTUAL IMAGE PAYLOAD', content_type='image/png')

        post_data = {
            'name': 'Corrupt File Wallet',
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,
            'leather_color': Design.COLOR_BROWN,
            'leather_finish': Design.FINISH_MATTE,
            'width': '11.5',
            'height': '9.0',
            'depth': '2.0',
            'stitching_color': Design.STITCH_BROWN,
            'logo': fake_png,
        }

        url = reverse('design_create', kwargs={'article_id': self.wallet_article.id})
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('logo' in response.context['form'].errors)
        self.assertEqual(Design.objects.filter(name='Corrupt File Wallet').count(), 0)

    def test_user_cannot_modify_or_remove_another_users_logo(self):
        """Test 8: User B cannot modify or clear User A's design logo."""
        logo_file = self._create_test_image(format='PNG', filename='alice_logo.png')
        alice_design = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Alice Branded Wallet',
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            logo=logo_file,
        )

        self.client.force_login(self.user_b)
        edit_url = reverse('design_edit', kwargs={'design_id': alice_design.id})

        # Bob attempts GET -> 404
        resp = self.client.get(edit_url)
        self.assertEqual(resp.status_code, 404)

        # Bob attempts POST clear_logo -> 404
        resp_post = self.client.post(edit_url, {'clear_logo': 'on', 'name': 'Hacked'})
        self.assertEqual(resp_post.status_code, 404)

        alice_design.refresh_from_db()
        self.assertTrue(bool(alice_design.logo))

    def test_duplicate_preserves_logo(self):
        """Test 9: Duplicating a design preserves the attached logo."""
        logo_file = self._create_test_image(format='PNG', filename='dup_logo.png')
        original = Design.objects.create(
            user=self.user_a,
            article=self.wallet_article,
            name='Original Branded Design',
            width=Decimal('11.5'),
            height=Decimal('9.0'),
            depth=Decimal('2.0'),
            logo=logo_file,
        )

        self.client.force_login(self.user_a)
        dup_url = reverse('design_duplicate', kwargs={'design_id': original.id})
        response = self.client.post(dup_url)
        self.assertEqual(response.status_code, 302)

        duplicate = Design.objects.get(name='Original Branded Design (Copy)')
        self.assertTrue(bool(duplicate.logo))
        self.assertEqual(duplicate.logo.name, original.logo.name)



from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class Article(models.Model):
    """
    Database model representing a customizable leather article category template.
    """
    CATEGORY_WALLETS = 'Wallets'
    CATEGORY_BELTS = 'Belts'
    CATEGORY_HANDBAGS = 'Handbags'
    CATEGORY_CARD_HOLDERS = 'Card Holders'
    CATEGORY_KEYCHAINS = 'Keychains'
    CATEGORY_POUCHES = 'Pouches'
    CATEGORY_LEATHER_COVERS = 'Leather Covers'

    CATEGORY_CHOICES = [
        (CATEGORY_WALLETS, 'Wallets'),
        (CATEGORY_BELTS, 'Belts'),
        (CATEGORY_HANDBAGS, 'Handbags'),
        (CATEGORY_CARD_HOLDERS, 'Card Holders'),
        (CATEGORY_KEYCHAINS, 'Keychains'),
        (CATEGORY_POUCHES, 'Pouches'),
        (CATEGORY_LEATHER_COVERS, 'Leather Covers'),
    ]

    name = models.CharField(
        max_length=200,
        help_text="Name of the leather article (e.g., Classic Leather Wallet)"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text="Product category for filtering and templates"
    )
    description = models.TextField(
        help_text="Detailed description of the leather product, dimensions, and craft details"
    )
    material = models.CharField(
        max_length=150,
        help_text="Primary leather type or material grade (e.g., Full Grain Leather)"
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Base starting price in INR (₹)"
    )
    image = models.ImageField(
        upload_to='articles/',
        blank=True,
        null=True,
        help_text="High-resolution product showcase image"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when article template was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when article template was last modified"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Leather Article"
        verbose_name_plural = "Leather Articles"

    def __str__(self):
        return f"{self.name} ({self.category})"


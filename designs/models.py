from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from articles.models import Article


class Design(models.Model):
    """
    Model representing an entrepreneur's custom leather article configuration.
    Links a specific Article template with chosen leather, dimension, stitching, and custom text specifications.
    """
    # Leather Type Choices
    LEATHER_TYPE_FULL_GRAIN = 'Full Grain Leather'
    LEATHER_TYPE_TOP_GRAIN = 'Top Grain Leather'
    LEATHER_TYPE_GENUINE = 'Genuine Leather'
    LEATHER_TYPE_SUEDE = 'Suede Leather'

    LEATHER_TYPE_CHOICES = [
        (LEATHER_TYPE_FULL_GRAIN, 'Full Grain Leather'),
        (LEATHER_TYPE_TOP_GRAIN, 'Top Grain Leather'),
        (LEATHER_TYPE_GENUINE, 'Genuine Leather'),
        (LEATHER_TYPE_SUEDE, 'Suede Leather'),
    ]

    # Leather Color Choices
    COLOR_BLACK = 'Black'
    COLOR_BROWN = 'Brown'
    COLOR_TAN = 'Tan'
    COLOR_DARK_BROWN = 'Dark Brown'
    COLOR_RED = 'Red'
    COLOR_BLUE = 'Blue'

    LEATHER_COLOR_CHOICES = [
        (COLOR_BLACK, 'Black'),
        (COLOR_BROWN, 'Brown'),
        (COLOR_TAN, 'Tan'),
        (COLOR_DARK_BROWN, 'Dark Brown'),
        (COLOR_RED, 'Red'),
        (COLOR_BLUE, 'Blue'),
    ]

    # Leather Finish Choices
    FINISH_MATTE = 'Matte'
    FINISH_SMOOTH = 'Smooth'
    FINISH_TEXTURED = 'Textured'
    FINISH_GLOSSY = 'Glossy'

    LEATHER_FINISH_CHOICES = [
        (FINISH_MATTE, 'Matte'),
        (FINISH_SMOOTH, 'Smooth'),
        (FINISH_TEXTURED, 'Textured'),
        (FINISH_GLOSSY, 'Glossy'),
    ]

    # Stitching Color Choices
    STITCH_BLACK = 'Black'
    STITCH_WHITE = 'White'
    STITCH_BROWN = 'Brown'
    STITCH_TAN = 'Tan'
    STITCH_RED = 'Red'

    STITCHING_COLOR_CHOICES = [
        (STITCH_BLACK, 'Black'),
        (STITCH_WHITE, 'White'),
        (STITCH_BROWN, 'Brown'),
        (STITCH_TAN, 'Tan'),
        (STITCH_RED, 'Red'),
    ]

    # Font Choices
    FONT_CLASSIC = 'Classic'
    FONT_MODERN = 'Modern'
    FONT_ELEGANT = 'Elegant'
    FONT_BOLD = 'Bold'

    FONT_CHOICES = [
        (FONT_CLASSIC, 'Classic'),
        (FONT_MODERN, 'Modern'),
        (FONT_ELEGANT, 'Elegant'),
        (FONT_BOLD, 'Bold'),
    ]

    # Text Size Choices
    TEXT_SIZE_CHOICES = [
        (12, '12 pt'),
        (14, '14 pt'),
        (16, '16 pt'),
        (18, '18 pt'),
        (20, '20 pt'),
        (24, '24 pt'),
        (28, '28 pt'),
        (32, '32 pt'),
    ]

    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='designs',
        help_text="The artisan/entrepreneur who created this design"
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='designs',
        help_text="The base leather article template"
    )

    # Core Specifications
    name = models.CharField(
        max_length=200,
        help_text="Custom name for this design (e.g., Classic Brown Wallet)"
    )
    leather_type = models.CharField(
        max_length=50,
        choices=LEATHER_TYPE_CHOICES,
        default=LEATHER_TYPE_FULL_GRAIN,
        help_text="Grade of leather chosen for fabrication"
    )
    leather_color = models.CharField(
        max_length=30,
        choices=LEATHER_COLOR_CHOICES,
        default=COLOR_BROWN,
        help_text="Primary leather dye / color"
    )
    leather_finish = models.CharField(
        max_length=30,
        choices=LEATHER_FINISH_CHOICES,
        default=FINISH_MATTE,
        help_text="Surface texture and sheen treatment"
    )

    # Dimensions in centimeters
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.1')), MaxValueValidator(Decimal('500.0'))],
        help_text="Article width in centimeters"
    )
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.1')), MaxValueValidator(Decimal('500.0'))],
        help_text="Article height in centimeters"
    )
    depth = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.1')), MaxValueValidator(Decimal('500.0'))],
        help_text="Article depth in centimeters"
    )

    # Customization & Embellishments
    stitching_color = models.CharField(
        max_length=30,
        choices=STITCHING_COLOR_CHOICES,
        default=STITCH_BROWN,
        help_text="Color of the edge and structural stitching"
    )
    custom_text = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Optional embossed text or brand name"
    )
    font = models.CharField(
        max_length=30,
        choices=FONT_CHOICES,
        default=FONT_CLASSIC,
        help_text="Typography style for embossed custom text"
    )
    text_size = models.PositiveIntegerField(
        choices=TEXT_SIZE_CHOICES,
        default=18,
        validators=[MinValueValidator(12), MaxValueValidator(32)],
        help_text="Font size in points for custom text"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when design was configured"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when design was last modified"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Custom Design"
        verbose_name_plural = "Custom Designs"

    def __str__(self):
        return f"{self.name} ({self.article.name}) - {self.user.username}"

from decimal import Decimal

# Leather Type Surcharges
LEATHER_SURCHARGES = {
    'Full Grain Leather': Decimal('150.00'),
    'Top Grain Leather': Decimal('100.00'),
    'Genuine Leather': Decimal('50.00'),
    'Suede Leather': Decimal('100.00'),
}

DEFAULT_STITCHING_COLOR = 'Black'
SPECIAL_STITCHING_SURCHARGE = Decimal('50.00')
CUSTOM_TEXT_SURCHARGE = Decimal('25.00')


def calculate_design_cost(base_price, leather_type='Full Grain Leather', stitching_color='Black', custom_text=''):
    """
    Authoritative backend cost estimation calculation using Decimal arithmetic.

    Formula:
      Estimated Total = Base Article Price + Leather Surcharge + Stitching Surcharge + Custom Text Surcharge

    Surcharges:
      - Leather:
          Full Grain Leather: ₹150.00
          Top Grain Leather:  ₹100.00
          Genuine Leather:    ₹50.00
          Suede Leather:      ₹100.00
      - Finish: ₹0.00 for all finishes (Matte, Smooth, Textured, Glossy)
      - Stitching: ₹50.00 when stitching_color differs from 'Black', otherwise ₹0.00
      - Custom Text: ₹25.00 when custom text is provided, otherwise ₹0.00
    """
    # Ensure base_price is Decimal
    if not isinstance(base_price, Decimal):
        try:
            base_price = Decimal(str(base_price))
        except Exception:
            base_price = Decimal('0.00')

    # 1. Leather surcharge
    leather_surcharge = LEATHER_SURCHARGES.get(leather_type, Decimal('0.00'))

    # 2. Stitching surcharge: ₹50 when differing from 'Black', else ₹0
    if stitching_color and str(stitching_color).strip().lower() != DEFAULT_STITCHING_COLOR.lower():
        stitching_surcharge = SPECIAL_STITCHING_SURCHARGE
    else:
        stitching_surcharge = Decimal('0.00')

    # 3. Custom text surcharge: ₹25 if provided and non-empty, else ₹0
    if custom_text and str(custom_text).strip():
        custom_text_surcharge = CUSTOM_TEXT_SURCHARGE
    else:
        custom_text_surcharge = Decimal('0.00')

    # Authoritative Total
    total_estimate = base_price + leather_surcharge + stitching_surcharge + custom_text_surcharge

    return {
        'base_price': base_price,
        'leather_surcharge': leather_surcharge,
        'stitching_surcharge': stitching_surcharge,
        'custom_text_surcharge': custom_text_surcharge,
        'total_estimate': total_estimate,
    }

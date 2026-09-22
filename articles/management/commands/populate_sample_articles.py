from decimal import Decimal
from django.core.management.base import BaseCommand
from articles.models import Article


class Command(BaseCommand):
    help = "Populate database with 7 realistic sample leather articles across all supported categories."

    def handle(self, *args, **options):
        sample_articles = [
            {
                'name': 'Classic Leather Wallet',
                'category': Article.CATEGORY_WALLETS,
                'material': 'Full Grain Vegetable-Tanned Leather',
                'base_price': Decimal('500.00'),
                'description': (
                    'A timeless bifold leather wallet featuring 6 dedicated card slots, '
                    'two hidden interior compartments, and a spacious cash bill section. '
                    'Hand-burnished edges with durable saddle-stitch craftsmanship.'
                ),
            },
            {
                'name': 'Classic Leather Belt',
                'category': Article.CATEGORY_BELTS,
                'material': 'Full Grain Bridle Leather',
                'base_price': Decimal('700.00'),
                'description': (
                    'A premium heavy-duty dress and casual belt crafted from 9-10 oz English bridle leather. '
                    'Fitted with solid antique brass buckle hardware and precision-bevelled edges.'
                ),
            },
            {
                'name': 'Everyday Leather Handbag',
                'category': Article.CATEGORY_HANDBAGS,
                'material': 'Top Grain Pull-Up Leather',
                'base_price': Decimal('2800.00'),
                'description': (
                    'A structured yet versatile everyday shoulder tote with gusseted base geometry, '
                    'magnetic snap closure, internal zippered organizer, and reinforced double-stitched leather handles.'
                ),
            },
            {
                'name': 'Minimal Card Holder',
                'category': Article.CATEGORY_CARD_HOLDERS,
                'material': 'Vegetable-Tanned Buttero Leather',
                'base_price': Decimal('350.00'),
                'description': (
                    'An ultra-slim front-pocket card sleeve designed to carry 4-6 cards and folded cash. '
                    'Features an ergonomic thumb cut-out for swift access.'
                ),
            },
            {
                'name': 'Leather Keychain',
                'category': Article.CATEGORY_KEYCHAINS,
                'material': 'Full Grain Latigo Leather',
                'base_price': Decimal('150.00'),
                'description': (
                    'A durable leather loop key fob with solid antique brass snap hook and heavy-duty split ring. '
                    'Ideal for belt loops, bag attachments, or workshop tool keys.'
                ),
            },
            {
                'name': 'Leather Utility Pouch',
                'category': Article.CATEGORY_POUCHES,
                'material': 'Oil-Tanned Cowhide Leather',
                'base_price': Decimal('850.00'),
                'description': (
                    'A spacious zippered dopp kit and utility pouch for grooming essentials, stationery, or crafting tools. '
                    'Features a smooth heavy-duty brass zipper and side grab loop.'
                ),
            },
            {
                'name': 'Leather Notebook Cover',
                'category': Article.CATEGORY_LEATHER_COVERS,
                'material': 'Waxed Horween Chromexcel Leather',
                'base_price': Decimal('950.00'),
                'description': (
                    'A refillable A5 journal and planner cover with integrated pen loop, inner business card slots, '
                    'and bookmark ribbon. Develops a rich, lustrous patina with everyday use.'
                ),
            },
        ]

        created_count = 0
        updated_count = 0

        for item in sample_articles:
            article, created = Article.objects.get_or_create(
                name=item['name'],
                defaults=item
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {article.name} ({article.category})"))
            else:
                # Update fields to ensure consistency
                for key, value in item.items():
                    setattr(article, key, value)
                article.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated: {article.name} ({article.category})"))

        self.stdout.write(self.style.SUCCESS(
            f"\nSample data process complete: {created_count} created, {updated_count} updated."
        ))

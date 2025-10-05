from django.core.management.base import BaseCommand
from expenses.models import Category


class Command(BaseCommand):
    help = 'Seed default expense categories with keywords'

    def handle(self, *args, **kwargs):
        """Create default categories if they don't exist"""

        default_categories = [
            {
                'name': 'Grocery',
                'keywords': ['bigbasket', 'bbnow', 'zepto', 'grofers', 'dmart', 'fresh', 'supermarket', 'grocery'],
                'icon': '🛒',
                'color': '#4CAF50'
            },
            {
                'name': 'Travel',
                'keywords': ['uber', 'rapido', 'ola', 'travel', 'flight', 'train', 'bus', 'metro', 'taxi'],
                'icon': '🚗',
                'color': '#2196F3'
            },
            {
                'name': 'Food',
                'keywords': ['zomato', 'swiggy', 'restaurant', 'food', 'cafe', 'eternal', 'dominos', 'pizza', 'mcdonald'],
                'icon': '🍔',
                'color': '#FF9800'
            },
            {
                'name': 'Rent',
                'keywords': ['rent'],
                'icon': '🏠',
                'color': '#9C27B0'
            },
            {
                'name': 'Shopping',
                'keywords': ['amazon', 'flipkart', 'myntra', 'shopping', 'mall', 'store'],
                'icon': '🛍️',
                'color': '#E91E63'
            },
            {
                'name': 'Utilities',
                'keywords': ['electricity', 'water', 'gas', 'recharge', 'mobile', 'internet', 'wifi', 'broadband'],
                'icon': '💡',
                'color': '#FFC107'
            },
            {
                'name': 'Entertainment',
                'keywords': ['netflix', 'prime', 'spotify', 'movie', 'cinema', 'theatre', 'gaming', 'subscription'],
                'icon': '🎬',
                'color': '#F44336'
            },
            {
                'name': 'Personal Transfer',
                'keywords': ['santosh', 'ravi kumar', 'chandra', 'share', 'payment to'],
                'icon': '💸',
                'color': '#607D8B'
            },
            {
                'name': 'Healthcare',
                'keywords': ['medical', 'hospital', 'pharmacy', 'doctor', 'medicine', 'health'],
                'icon': '🏥',
                'color': '#00BCD4'
            },
            {
                'name': 'Miscellaneous',
                'keywords': ['google', 'other', 'misc'],
                'icon': '📦',
                'color': '#9E9E9E'
            },
        ]

        created_count = 0
        updated_count = 0

        for cat_data in default_categories:
            category, created = Category.objects.update_or_create(
                name=cat_data['name'],
                is_default=True,
                user=None,
                defaults={
                    'keywords': cat_data['keywords'],
                    'icon': cat_data.get('icon'),
                    'color': cat_data.get('color')
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated category: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone! Created {created_count} categories, updated {updated_count} categories.'
            )
        )

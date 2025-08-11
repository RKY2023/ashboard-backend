import os
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogs.settings')
django.setup()

from product.models import Product  # adjust import if model is elsewhere

# Product data from your JSON
products_data = [
    {"id": 1, "product_name": "Wireless Mouse", "product_code": "WM-001", "selling_price": 899, "purchase_price": 600, "created_at": "2025-08-06 05:57:42.606257", "updated_at": "2025-08-06 06:02:59.965183"},
    {"id": 4, "product_name": "New Name", "product_code": "P123", "selling_price": 200, "purchase_price": 150, "created_at": "2025-08-06 06:03:56.966873", "updated_at": "2025-08-06 12:17:32.101322"},
    {"id": 5, "product_name": "27 Monitor", "product_code": "MN-005", "selling_price": 15999, "purchase_price": 12999, "created_at": "2025-08-06 06:04:16.221328", "updated_at": "2025-08-06 06:04:16.221388"},
    {"id": 6, "product_name": "External SSD 1Tb", "product_code": "SSD-0076", "selling_price": 8000, "purchase_price": 7000, "created_at": "2025-08-06 06:04:47.728669", "updated_at": "2025-08-06 06:04:47.728690"},
    {"id": 7, "product_name": "Webcam HD", "product_code": "WC-0009", "selling_price": 1799, "purchase_price": 1400, "created_at": "2025-08-06 06:05:10.788722", "updated_at": "2025-08-06 06:05:10.788750"},
    {"id": 8, "product_name": "Noise Cancelling Headphones", "product_code": "NC-001", "selling_price": 10999, "purchase_price": 8500, "created_at": "2025-08-06 06:05:54.290733", "updated_at": "2025-08-06 06:05:54.290789"},
    {"id": 9, "product_name": "Graphic Tablet", "product_code": "GT-09", "selling_price": 4999, "purchase_price": 3800, "created_at": "2025-08-06 06:06:22.113394", "updated_at": "2025-08-06 06:06:22.113479"},
    {"id": 10, "product_name": "Bluetooth Speaker", "product_code": "BS-007", "selling_price": 2499, "purchase_price": 6500, "created_at": "2025-08-06 06:06:44.099038", "updated_at": "2025-08-06 06:06:44.099072"},
    {"id": 11, "product_name": "Laptop Stand", "product_code": "LS-0078", "selling_price": 1599, "purchase_price": 850, "created_at": "2025-08-06 07:29:22.234881", "updated_at": "2025-08-06 07:29:22.234900"},
    {"id": 12, "product_name": "Modem", "product_code": "MD-0098", "selling_price": 1500, "purchase_price": 700, "created_at": "2025-08-06 11:16:24.405568", "updated_at": "2025-08-06 11:16:24.405589"},
    {"id": 13, "product_name": "Mouse", "product_code": "BX0023", "selling_price": 124, "purchase_price": 123, "created_at": "2025-08-06 12:13:44.185268", "updated_at": "2025-08-06 12:13:44.185303"},
    {"id": 14, "product_name": "Mouse", "product_code": "BX0023", "selling_price": 124, "purchase_price": 123, "created_at": "2025-08-06 12:17:50.760539", "updated_at": "2025-08-06 12:17:50.760572"},
    {"id": 15, "product_name": "Tester", "product_code": "Testing", "selling_price": 100, "purchase_price": 20, "created_at": "2025-08-11 06:18:13.445475", "updated_at": "2025-08-11 06:18:13.445496"},
]

# Insert products
for data in products_data:
    Product.objects.update_or_create(
        id=data["id"],
        defaults={
            "product_name": data["product_name"],
            "product_code": data["product_code"],
            "selling_price": data["selling_price"],
            "purchase_price": data["purchase_price"],
            "created_at": datetime.fromisoformat(data["created_at"]),
            "updated_at": datetime.fromisoformat(data["updated_at"]),
        }
    )

print("✅ Products inserted/updated successfully!")

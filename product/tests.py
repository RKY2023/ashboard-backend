from django.test import TestCase

# Create your tests here.
class ProductTestCase(TestCase):
    def setUp(self):
        # Setup code to create a product instance for testing
        from product.models import Product
        self.product = Product.objects.create(
            product_name='Test Product',
            product_code='TP001',
            selling_price=100.00,
            purchase_price=80.00
        )

    def test_product_creation(self):
        # Test if the product was created successfully
        self.assertEqual(self.product.product_name, 'Test Product')
        self.assertEqual(self.product.product_code, 'TP001')
        self.assertEqual(self.product.selling_price, 100.00)
        self.assertEqual(self.product.purchase_price, 80.00)

    def test_product_str(self):
        # Test the string representation of the product
        self.assertEqual(str(self.product), 'Test Product')
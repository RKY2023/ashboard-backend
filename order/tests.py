from django.test import TestCase
from django.urls import reverse
from user.models import User
from order.models import Order
# Create your tests here.
class UserOrderTestCase(TestCase):
    # User = get_user_model()
    def setUp(self):
        # Set up any necessary data for the tests
        user = User.objects.create_user(
            username='testuser',
            password='testpassword')
        self.user = user
        self.order = Order.objects.create(
            vendor=user,
            status='Pending')
        
        pass

    def test_user_order_creation(self):
        # Test creating a user order
        user = User.Objects.get(username='testuser')
        self.client.force_login(user)
        response = self.client.get(reverse('user-order'))
        
        assert response.status_code == 200
        data = response.json()
        print(data)
        pass

    def test_user_order_retrieval(self):
        # Test retrieving user orders
        pass

    def test_user_order_deletion(self):
        # Test deleting a user order
        pass

    def tearDown(self):
        # Clean up after tests
        pass
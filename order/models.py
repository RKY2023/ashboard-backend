from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class OrderQuerySet(models.QuerySet):
    def approved(self):
        return self.filter(status='Approved')

    def locked(self):
        return self.filter(is_locked=True)

    def approvable_by(self, user):
        if user.has_perm('order.can_approve'):
            return self.exclude(status='Approved')
        return self.none()

    def lockable_by(self, user):
        if user.has_perm('order.can_lock'):
            return self.filter(is_locked=False)
        return self.none()


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def approved(self):
        return self.get_queryset().approved()

    def locked(self):
        return self.get_queryset().locked()

    def approvable_by(self, user):
        return self.get_queryset().approvable_by(user)

    def lockable_by(self, user):
        return self.get_queryset().lockable_by(user)


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    ]

    vendor = models.ForeignKey('vendor.Vendor', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending', choices=ORDER_STATUS_CHOICES)

    objects = OrderManager()

    def __str__(self):
        return f"Order {self.id} - {self.status} for {self.vendor}"

    @property
    def total_qty(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amt(self):
        return sum(item.total_price for item in self.items.all())

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        permissions = [
            ('can_approve', 'Can approve Order'),
            ('can_lock', 'Can lock Order'),
        ]


class OrderItem(models.Model):
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, blank=True, null=True)

    @property
    def total_price(self):
        return self.product.selling_price * self.quantity

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

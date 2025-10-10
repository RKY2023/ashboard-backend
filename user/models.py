from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """Custom user manager that supports email as the primary identifier"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password"""
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)

        # If username not provided, it will be auto-generated in save()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Create your models here.
class User(AbstractUser):
    # Email is now mandatory and unique - primary identifier
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        help_text="Email address - required and must be unique"
    )

    # Username is optional but must be unique if provided
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text="Username - optional but must be unique if provided"
    )

    mobile = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{0,3}?\d{9,15}$',
                message="Phone no must be in 10 digits. Add country code if needed.",
            ),
        ]
    )
    date_of_birth = models.DateField(blank=True, null=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_user = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='created_by_parent',
        blank=True,
        null=True,
        default=None
    )
    address = models.CharField(max_length=500, blank=True, null=True)
    mobile_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    # Use email as the primary login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove username from required fields

    # Use custom manager
    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Override save to auto-create username from email if not provided"""
        if not self.username:
            # Generate username from email (part before @)
            self.username = self.email.split('@')[0]

            # Ensure uniqueness by adding numbers if needed
            base_username = self.username
            counter = 1
            while User.objects.filter(username=self.username).exclude(pk=self.pk).exists():
                self.username = f"{base_username}{counter}"
                counter += 1

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
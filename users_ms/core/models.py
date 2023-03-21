from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils import timezone


# UserRole model
class UserRole(models.Model):
    ROLE_BUYER = "B"
    ROLE_SELLER = "S"
    ROLE_ADMIN = "A"
    ROLE_CHOICES = [
        (ROLE_BUYER, "Buyer"),
        (ROLE_SELLER, "Seller"),
        (ROLE_ADMIN, "Admin"),
    ]

    user_role_name = models.CharField(max_length=1, choices=ROLE_CHOICES)


# Manager for the Custom User model
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    # Create regular user ( Buyer or Seller )
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    # Create admin user
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_role_id", 3)
        return self._create_user(email, password, **extra_fields)


# Custom User model
class User(AbstractBaseUser, PermissionsMixin):
    # Enum type iterable for gender choices
    GENDER_MALE = "M"
    GENDER_FEMALE = "F"
    GENDER_OTHER = "O"
    GENDER_CHOICES = [
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    ]

    # Custom fields
    first_name = models.CharField(max_length=255, blank=True, default="")
    last_name = models.CharField(max_length=255, blank=True, default="")
    email = models.EmailField(blank=True, default="", unique=True)
    username = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default=GENDER_OTHER
    )
    user_role = models.ForeignKey(UserRole, on_delete=models.CASCADE)

    # Django user fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # Linking manager to model
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username", "date_of_birth", "gender"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_full_name(self):
        return self.first_name + self.last_name

    def get_short_name(self):
        return self.first_name + self.last_name or self.email.split("@")[0]


# Address model
class Address(models.Model):
    # Address fields
    address_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    door_no = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    pincode = models.IntegerField()

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    image = models.ImageField(upload_to='User_imgs/', default='default.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('User', 'User'),
        ('Agent', 'Agent'),
        ('Caissier', 'Caissier'),
    )
    role = models.TextField(max_length=10, choices=ROLE_CHOICES, default='Admin')

    def __str__(self):
        return self.username

class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset request for {self.user}"
    

class ProxyAccounts(User):
    class Meta:
        proxy = True
        verbose_name = 'ProxyAccount'
        verbose_name_plural = 'ProxyAccounts'
        
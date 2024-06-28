from django.db import models
from login.models import User
import uuid

class Category(models.Model):
    name = models.CharField(max_length=255)

class Advertisement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_budget = models.DecimalField(max_digits=10, decimal_places=2)
    per_job = models.DecimalField(max_digits=10, decimal_places=2)
    limit = models.CharField(max_length=10, choices=[('days', 'Days'), ('jobs', 'Jobs')])
    description = models.TextField()
    confirmation_requirements = models.TextField()
    requires_media = models.BooleanField(default=False)
    media_type = models.CharField(max_length=10, choices=[('photo', 'Photo'), ('video', 'Video'), ('both', 'Both')],
                                  null=True, blank=True)
    status = models.CharField(max_length=10, default='active')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    terminate = models.DateField()

class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class UserTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('earn', 'Earn'),
        ('spend', 'Spend')
    ]
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(Advertisement, null=True, blank=True, on_delete=models.SET_NULL)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='pending')

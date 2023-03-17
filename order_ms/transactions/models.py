from django.db import models

# Create your models here.
class Transaction(models.Model):
    
    transaction_id = models.BigIntegerField(primary_key=True)
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    payment_type = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=255)
    payment_time = models.DateTimeField()
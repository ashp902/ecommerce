from django.db import models

from transactions.models import Transaction

# Create your models here.
class Order(models.Model):
    
    user_id = models.BigIntegerField()
    address_id = models.BigIntegerField()
    placed_time = models.DateTimeField()
    updated_time = models.DateTimeField()
    delivery_status = models.CharField(max_length=255)
    total_amount = models.FloatField()
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

class OrderItem(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.BigIntegerField()
    price = models.FloatField()
    discount = models.FloatField()
    quantity = models.IntegerField()
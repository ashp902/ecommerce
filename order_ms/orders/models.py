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

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "address_id": self.address_id,
            "delivery_status": self.delivery_status,
            "total_amount": self.total_amount,
        }


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.BigIntegerField()
    price = models.FloatField()
    discount = models.FloatField()
    quantity = models.IntegerField()

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "price": self.price,
            "discount": self.discount,
            "quantity": self.quantity,
        }

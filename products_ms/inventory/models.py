from django.db import models

from products.models import Product


# Create your models here.
class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField()
    price = models.FloatField()
    discount = models.FloatField()
    last_stocked = models.DateTimeField()
    last_updated = models.DateTimeField()

    def to_dict(self):
        return {
            "product": self.product_id,
            "count": self.count,
            "price": self.price,
            "discount": self.discount,
        }

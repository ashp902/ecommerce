from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Product(models.Model):

    product_name = models.CharField(max_length=255)
    product_description = models.TextField()
    product_tags = ArrayField(models.CharField(max_length=255))
    seller_id = models.BigIntegerField()
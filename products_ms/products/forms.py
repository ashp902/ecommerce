from django import forms
from django.contrib.postgres.forms import SimpleArrayField

from datetime import datetime

from .models import Product
from inventory.models import InventoryItem


class ProductForm(forms.Form):
    product_name = forms.CharField(max_length=255)
    product_description = forms.CharField(widget=forms.Textarea)
    products_tags = SimpleArrayField(forms.CharField(max_length=255))

    product_count = forms.IntegerField()
    price = forms.FloatField()
    discount = forms.FloatField()

    def save(self):
        data = self.cleaned_data
        product = Product(
            product_name=data["product_name"],
            product_description=data["product_description"],
            products_tags=data["products_tags"],
        )
        product.save()
        inventory_item = InventoryItem(
            product_id=product.id,
            product_count=data["product_count"],
            price=data["price"],
            last_stocked=datetime.now(),
            discount=data["discount"],
        )
        inventory_item.save()

from django import forms
from django.contrib.postgres.forms import SimpleArrayField

class ProductForm(forms.Form):

    product_name = forms.CharField(max_length=255)
    product_description = forms.CharField(widget=forms.Textarea)
    product_tags = SimpleArrayField(forms.CharField(max_length=255))

    product_count = forms.IntegerField()
    price = forms.FloatField()
    discount = forms.FloatField()

    delete = forms.BooleanField(required=False)

class OrderForm(forms.Form):
    # addresses = [(1, '1')]

    # name = forms.CharField(max_length=255)
    # address = forms.ChoiceField(choices=addresses)

    def __init__(self, addresses):
        super(forms.Form, self).__init__()
        self.addresses = addresses
        self.address = forms.ChoiceField(choices=self.addresses)
    
    class Meta:
        fields =['address']
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

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields["product_name"].widget.attrs["placeholder"] = "Product name"
        self.fields["product_description"].widget.attrs[
            "placeholder"
        ] = "Product description"
        self.fields["product_tags"].widget.attrs["placeholder"] = "Product tags"
        self.fields["product_count"].widget.attrs["placeholder"] = "Product count"
        self.fields["price"].widget.attrs["placeholder"] = "Price"
        self.fields["discount"].widget.attrs["placeholder"] = "Discount"


class OrderForm(forms.Form):
    # addresses = [(1, '1')]

    # name = forms.CharField(max_length=255)
    # address = forms.ChoiceField(choices=addresses)

    def __init__(self, addresses):
        super(forms.Form, self).__init__()
        self.addresses = addresses
        self.address = forms.ChoiceField(choices=self.addresses)

    class Meta:
        fields = ["address"]

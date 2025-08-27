from django import forms
from .models import Customer, Sale, Return
from products.models import Product

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name","last_name","email","phone","address"]

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["customer","product","quantity","unit_price"]

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ["sale","product","quantity","return_reason"]

from django import forms
from django.core.exceptions import ValidationError
from .models import Product

class ProductForm(forms.ModelForm):
    """Form for adding and updating products - replaces your tkinter dialogs"""
    
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'price', 'stock_quantity', 'min_threshold', 'description']
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'min_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '10'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Product description (optional)'
            })
        }
    
    def clean_product_name(self):
        """Validate product name uniqueness - like your original validation"""
        product_name = self.cleaned_data.get('product_name')
        if product_name:
            # Check for duplicates, excluding current instance if updating
            queryset = Product.objects.filter(product_name__iexact=product_name)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError("A product with this name already exists.")
        
        return product_name
    
    def clean_price(self):
        """Validate price - like your original validation"""
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise ValidationError("Price cannot be negative.")
        return price


class ProductSearchForm(forms.Form):
    """Search form - replaces your tkinter search functionality"""
    search_query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...',
            'id': 'searchInput'
        })
    )
    category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by category...'
        })
    )